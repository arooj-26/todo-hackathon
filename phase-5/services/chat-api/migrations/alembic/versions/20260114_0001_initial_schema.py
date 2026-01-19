"""Initial schema migration.

Revision ID: 20260114_0001
Revises:
Create Date: 2026-01-14

This migration creates the initial database schema for the Chat API service:
- users: User accounts with timezone and notification preferences
- tasks: Tasks with status, priority, due dates, and full-text search
- recurrence_patterns: Recurring task configuration
- tags: Task categorization labels
- task_tags: Many-to-many relationship between tasks and tags
- reminders: Scheduled task notifications
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260114_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema tables."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('notification_preferences', sa.JSON(), nullable=True,
                  server_default='{"email": true, "push": false, "in_app": true}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='todo'),
        sa.Column('priority', sa.String(length=10), nullable=False, server_default='medium'),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('recurrence_pattern_id', sa.Integer(), nullable=True),
        sa.Column('parent_task_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_due_at', 'tasks', ['due_at'])
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'])

    # Create recurrence_patterns table
    op.create_table(
        'recurrence_patterns',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('pattern_type', sa.String(length=20), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('days_of_week', sa.JSON(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('end_condition', sa.String(length=20), nullable=False),
        sa.Column('occurrence_count', sa.Integer(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('current_occurrence', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id')
    )

    # Add foreign key from tasks to recurrence_patterns (circular reference)
    op.create_foreign_key(
        'fk_tasks_recurrence_pattern_id',
        'tasks', 'recurrence_patterns',
        ['recurrence_pattern_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_tags_name', 'tags', ['name'])
    op.create_index('ix_tags_usage_count', 'tags', ['usage_count'])

    # Create task_tags join table
    op.create_table(
        'task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )

    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('remind_at', sa.DateTime(), nullable=False),
        sa.Column('notification_channel', sa.String(length=20), nullable=False, server_default='in_app'),
        sa.Column('delivery_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminders_task_id', 'reminders', ['task_id'])
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'])
    op.create_index('ix_reminders_remind_at', 'reminders', ['remind_at'])
    op.create_index('ix_reminders_delivery_status', 'reminders', ['delivery_status'])

    # Add full-text search vector column (PostgreSQL specific)
    op.execute("""
        ALTER TABLE tasks ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        ) STORED
    """)
    op.execute("CREATE INDEX ix_tasks_search_vector ON tasks USING GIN (search_vector)")


def downgrade() -> None:
    """Drop all tables in reverse order."""

    # Drop full-text search index and column
    op.execute("DROP INDEX IF EXISTS ix_tasks_search_vector")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS search_vector")

    # Drop tables in reverse dependency order
    op.drop_table('reminders')
    op.drop_table('task_tags')
    op.drop_table('tags')

    # Drop foreign key before dropping recurrence_patterns
    op.drop_constraint('fk_tasks_recurrence_pattern_id', 'tasks', type_='foreignkey')
    op.drop_table('recurrence_patterns')

    op.drop_table('tasks')
    op.drop_table('users')
