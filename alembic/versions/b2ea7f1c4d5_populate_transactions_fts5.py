"""Populate transactions_fts for existing transactions

Revision ID: b2ea7f1c4d5
Revises: a1f2c3d4e5f6
Create Date: 2026-05-17 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from backend.fts_utils import build_fts_ngram_text


# revision identifiers, used by Alembic.
revision: str = 'b2ea7f1c4d5'
down_revision: Union[str, None] = 'a1f2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Populate transactions_fts with existing transaction names as n-gram tokens.
    bind = op.get_bind()
    raw_conn = bind.connection
    select_cur = raw_conn.cursor()
    insert_cur = raw_conn.cursor()

    batch_size = 1000
    select_cur.execute("SELECT id, name FROM transactions ORDER BY id")

    while True:
        batch = select_cur.fetchmany(batch_size)

        if not batch:
            break

        for row_id, name in batch:
            insert_cur.execute(
                "INSERT INTO transactions_fts(rowid, name) VALUES (?, ?)",
                (row_id, build_fts_ngram_text(name)),
            )

        raw_conn.commit()


def downgrade() -> None:
    # Clear the FTS table.
    op.execute(sa.text("DELETE FROM transactions_fts"))
