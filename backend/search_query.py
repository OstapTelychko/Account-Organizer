from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import select
from datetime import date
from rapidfuzz import process, fuzz

from backend.models import Transaction, TransactionsFTS
from backend.fts_utils import build_fts_ngram_text

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session
    from sqlalchemy.sql.elements import BinaryExpression
    from typing import Any, Callable




class SearchQuery:
    """This class is used to manage search queries."""

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int

        self.values_operands: dict[str, Callable[[Any, Any], BinaryExpression[Any]]] = {
            "=": lambda field, value: field == value,
            "!=": lambda field, value: field != value,
            "<": lambda field, value: field < value,
            ">": lambda field, value: field > value,
            "<=": lambda field, value: field <= value,
            ">=": lambda field, value: field >= value,
        }
    

    def search_transactions(
            self,
            name_substring:str,
            value:float|None,
            value_operand:str,
            from_date:date,
            to_date:date,
            categories_id:list[int]
        ) -> list[Transaction]:
        """Search for transactions based on name, value, date range, and categories.

            Arguments
            ---------
                `name_substring` : (str) - Substring to search in transaction names.
                `value` : (float) - Value to search in transaction values.
                `value_operand` : (str) - Operand to use for value comparison.
                `from_date` : (date) - Start date of the date range.
                `to_date` : (date) - End date of the date range.
                `categories_id` : (list[int]) - List of category IDs to filter transactions.
        """
        # Build common filters
        filters = [
            Transaction.date.between(from_date, to_date),
            Transaction.category_id.in_(categories_id)
        ]

        if value:
            operand_func = self.values_operands[value_operand]
            filters.append(operand_func(Transaction.value, value))

        # Build base query using FTS5 if name_substring provided, otherwise plain query
        if name_substring:
            # Use FTS5 virtual table for Unicode-aware search (pure DB-side).
            
            fts = TransactionsFTS.__table__
            fts_tokens = build_fts_ngram_text(name_substring).split()
            fts_query = " OR ".join(f'"{token}"' for token in fts_tokens) if fts_tokens else ""

            stmt = select(Transaction).select_from(
                Transaction.__table__.join(fts, fts.c.rowid == Transaction.__table__.c.id)
            )
            if fts_query:
                stmt = stmt.where(fts.c.name.match(fts_query))
        else:
            stmt = select(Transaction)

        # Apply common filters to both FTS and non-FTS queries
        stmt = stmt.where(*filters)

        # Apply ordering based on search type
        if not name_substring and value:
            # Order by value if value filter is applied
            if value_operand in (">=", ">"):
                stmt = stmt.order_by(Transaction.value.asc())
            elif value_operand in ("<=", "<", "!="):
                stmt = stmt.order_by(Transaction.value.desc())

        with self.session_factory() as session:
            with session.begin():
                results = list(session.execute(stmt).scalars())

                # SQLite's built-in case-insensitive functions and collations are
                # ASCII-only in many builds and may not handle Unicode casefolding
                # correctly. Therefore, we do Unicode-aware ranking and filtering in Python
                # using RapidFuzz for typo tolerance and proper substring matching.
                if name_substring and results:
                    search_query_casefolded = name_substring.casefold()
                    
                    transaction_names = [(t.name or "").casefold() for t in results]
                    
                    extracted = process.extract(
                        query=search_query_casefolded,
                        choices=transaction_names,
                        scorer=fuzz.WRatio,
                        score_cutoff=85,  # Filters out candidates without typo-tolerant substring match
                        limit=None
                    )
                    
                    # 'extracted' returns Tuples of (matched_string, match_score, index)
                    # Sort primarily by match score (highest first).
                    # Secondary sort ensures stable tie-breaking.
                    extracted.sort(key=lambda x: (-x[1], x[0]))
                    
                    results = [results[match_data[2]] for match_data in extracted]

                return results
