"""Add FTS5 virtual table for transactions.name

Revision ID: a1f2c3d4e5f6
Revises: 98603936a4ff
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union, Any, cast

from alembic import op
import sqlalchemy as sa
from sqlalchemy import DDL


# revision identifiers, used by Alembic.
revision: str = 'a1f2c3d4e5f6'
down_revision: Union[str, None] = '98603936a4ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create FTS5 virtual table for n-gram tokens stored by the application.
    op.execute(cast(Any, DDL)(
        "CREATE VIRTUAL TABLE transactions_fts "
        "USING fts5(name, tokenize='unicode61 remove_diacritics 1')"
    ))


def downgrade() -> None:
    op.execute(cast(Any, DDL)("DROP TABLE IF EXISTS transactions_fts"))
