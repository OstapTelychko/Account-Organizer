"""Add investments (transaction operation type and account level reminders)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add `transactions.operation_type` and make monthly reminders belong to an account."""

    # Plain ADD COLUMN keeps the transactions table (and its FTS triggers) untouched
    op.add_column(
        'transactions',
        sa.Column('operation_type', sa.SmallInteger(), nullable=False, server_default='0')
    )

    op.add_column('monthly_reminders', sa.Column('account_id', sa.Integer(), nullable=True))
    op.add_column(
        'monthly_reminders',
        sa.Column('reminder_type', sa.SmallInteger(), nullable=False, server_default='0')
    )
    op.execute(
        "UPDATE monthly_reminders SET account_id = "
        "(SELECT categories.account_id FROM categories WHERE categories.id = monthly_reminders.category_id)"
    )

    with op.batch_alter_table('monthly_reminders') as batch_op:
        batch_op.alter_column('account_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('category_id', existing_type=sa.Integer(), nullable=True)
        batch_op.create_foreign_key(
            'fk_monthly_reminders_account_id', 'accounts', ['account_id'], ['id'], ondelete='CASCADE'
        )
        batch_op.create_check_constraint(
            'ck_monthly_reminders_category_by_type', '(reminder_type = 0) = (category_id IS NOT NULL)'
        )
        batch_op.create_index('ix_monthly_reminders_account_id', ['account_id'])


def downgrade() -> None:
    """Remove investments reminders and the added columns."""

    op.execute("DELETE FROM monthly_reminders WHERE reminder_type != 0")

    with op.batch_alter_table('monthly_reminders') as batch_op:
        batch_op.drop_index('ix_monthly_reminders_account_id')
        batch_op.drop_constraint('ck_monthly_reminders_category_by_type', type_='check')
        batch_op.drop_constraint('fk_monthly_reminders_account_id', type_='foreignkey')
        batch_op.alter_column('category_id', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column('reminder_type')
        batch_op.drop_column('account_id')

    op.drop_column('transactions', 'operation_type')
