"""Add monthly_reminders table

Revision ID: c3d4e5f6a7b8
Revises: b2ea7f1c4d5
Create Date: 2026-10-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2ea7f1c4d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the monthly_reminders table."""

    op.create_table(
        'monthly_reminders',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('day', sa.SmallInteger(), nullable=True),
        sa.Column('next_due_date', sa.Date(), nullable=False),
        sa.Column(
            'category_id',
            sa.Integer(),
            sa.ForeignKey('categories.id', ondelete='CASCADE'),
            nullable=False
        ),
    )
    op.create_index('ix_monthly_reminders_category_id', 'monthly_reminders', ['category_id'])


def downgrade() -> None:
    """Drop the monthly_reminders table."""

    op.drop_index('ix_monthly_reminders_category_id', table_name='monthly_reminders')
    op.drop_table('monthly_reminders')
