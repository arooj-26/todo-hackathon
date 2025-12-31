"""Add due_date and recurrence fields to tasks

Revision ID: 2025_12_26_1000
Revises: 8f09b42702fa
Create Date: 2025-12-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '2025_12_26_1000'
down_revision = '8f09b42702fa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add due_date column (nullable)
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    
    # Add recurrence column (nullable)
    op.add_column('tasks', sa.Column('recurrence', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True))


def downgrade() -> None:
    # Drop recurrence column
    op.drop_column('tasks', 'recurrence')
    
    # Drop due_date column
    op.drop_column('tasks', 'due_date')