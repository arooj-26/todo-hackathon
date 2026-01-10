-- Phase V: Advanced Cloud Deployment - Initial Schema
-- Database: PostgreSQL 16+
-- Date: 2026-01-05

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search support
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- Table: users
-- =============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    notification_preferences JSONB NOT NULL DEFAULT '{"email": true, "push": false, "in_app": true}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT username_format CHECK (username ~ '^[a-zA-Z0-9_-]{3,50}$'),
    CONSTRAINT email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- =============================================================================
-- Table: tasks
-- =============================================================================
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'todo',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    due_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recurrence_pattern_id INTEGER,
    parent_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
    ) STORED,

    CONSTRAINT status_values CHECK (status IN ('todo', 'in_progress', 'completed')),
    CONSTRAINT priority_values CHECK (priority IN ('high', 'medium', 'low')),
    CONSTRAINT completed_at_when_completed CHECK (
        (status = 'completed' AND completed_at IS NOT NULL) OR
        (status != 'completed' AND completed_at IS NULL)
    ),
    CONSTRAINT not_both_parent_and_recurring CHECK (
        NOT (recurrence_pattern_id IS NOT NULL AND parent_task_id IS NOT NULL)
    )
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_at ON tasks(due_at) WHERE due_at IS NOT NULL;
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_search_vector ON tasks USING GIN(search_vector);
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id) WHERE parent_task_id IS NOT NULL;

-- =============================================================================
-- Table: recurrence_patterns
-- =============================================================================
CREATE TABLE recurrence_patterns (
    id SERIAL PRIMARY KEY,
    task_id INTEGER UNIQUE NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    pattern_type VARCHAR(10) NOT NULL,
    interval INTEGER NOT NULL DEFAULT 1,
    days_of_week INTEGER[],
    day_of_month INTEGER,
    end_condition VARCHAR(20) NOT NULL,
    occurrence_count INTEGER,
    current_occurrence INTEGER NOT NULL DEFAULT 0,
    end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT pattern_type_values CHECK (pattern_type IN ('daily', 'weekly', 'monthly')),
    CONSTRAINT interval_range CHECK (interval >= 1 AND interval <= 365),
    CONSTRAINT end_condition_values CHECK (end_condition IN ('never', 'after_occurrences', 'by_date')),
    CONSTRAINT days_of_week_range CHECK (
        days_of_week IS NULL OR
        (array_length(days_of_week, 1) > 0 AND
         days_of_week <@ ARRAY[0,1,2,3,4,5,6])
    ),
    CONSTRAINT day_of_month_range CHECK (day_of_month IS NULL OR (day_of_month >= 1 AND day_of_month <= 31)),
    CONSTRAINT occurrence_count_when_needed CHECK (
        (end_condition = 'after_occurrences' AND occurrence_count IS NOT NULL) OR
        (end_condition != 'after_occurrences')
    ),
    CONSTRAINT end_date_when_needed CHECK (
        (end_condition = 'by_date' AND end_date IS NOT NULL) OR
        (end_condition != 'by_date')
    )
);

CREATE INDEX idx_recurrence_patterns_task_id ON recurrence_patterns(task_id);

-- =============================================================================
-- Table: tags
-- =============================================================================
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT tag_name_format CHECK (name ~ '^[a-z0-9-]+$')
);

CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_usage_count ON tags(usage_count DESC);

-- =============================================================================
-- Table: task_tags (Many-to-Many relationship)
-- =============================================================================
CREATE TABLE task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);

-- =============================================================================
-- Table: reminders
-- =============================================================================
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    remind_at TIMESTAMPTZ NOT NULL,
    delivery_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notification_channel VARCHAR(20) NOT NULL DEFAULT 'in_app',
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT delivery_status_values CHECK (delivery_status IN ('pending', 'sent', 'failed', 'cancelled')),
    CONSTRAINT notification_channel_values CHECK (notification_channel IN ('in_app', 'email', 'sms')),
    CONSTRAINT retry_count_range CHECK (retry_count >= 0 AND retry_count <= 10)
);

CREATE INDEX idx_reminders_task_id ON reminders(task_id);
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_remind_at ON reminders(remind_at) WHERE delivery_status = 'pending';
CREATE INDEX idx_reminders_status ON reminders(delivery_status);

-- =============================================================================
-- Table: audit_logs
-- =============================================================================
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    task_id INTEGER,
    user_id UUID,
    event_data JSONB NOT NULL,
    correlation_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT event_type_values CHECK (event_type IN ('created', 'updated', 'completed', 'deleted', 'reminder_sent'))
);

CREATE INDEX idx_audit_logs_task_id ON audit_logs(task_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_correlation_id ON audit_logs(correlation_id);
CREATE INDEX idx_audit_logs_event_data ON audit_logs USING GIN(event_data);

-- =============================================================================
-- Triggers
-- =============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recurrence_patterns_updated_at BEFORE UPDATE ON recurrence_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reminders_updated_at BEFORE UPDATE ON reminders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update tag usage_count when task_tags changes
CREATE OR REPLACE FUNCTION update_tag_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE tags SET usage_count = usage_count + 1 WHERE id = NEW.tag_id;
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE tags SET usage_count = GREATEST(usage_count - 1, 0) WHERE id = OLD.tag_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tag_usage_on_insert AFTER INSERT ON task_tags
    FOR EACH ROW EXECUTE FUNCTION update_tag_usage_count();

CREATE TRIGGER update_tag_usage_on_delete AFTER DELETE ON task_tags
    FOR EACH ROW EXECUTE FUNCTION update_tag_usage_count();

-- =============================================================================
-- Sample Data (for development/testing)
-- =============================================================================

-- Create a default user
INSERT INTO users (id, username, email, timezone) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'demo_user', 'demo@todochatbot.com', 'America/Los_Angeles')
ON CONFLICT DO NOTHING;

-- Create some default tags
INSERT INTO tags (name) VALUES
    ('work'),
    ('personal'),
    ('urgent'),
    ('backend'),
    ('frontend')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Comments
-- =============================================================================

COMMENT ON TABLE users IS 'User accounts with timezone and notification preferences';
COMMENT ON TABLE tasks IS 'Tasks with full-text search, priorities, tags, and recurrence support';
COMMENT ON TABLE recurrence_patterns IS 'Recurrence rules for repeating tasks (daily/weekly/monthly)';
COMMENT ON TABLE tags IS 'Reusable labels for task categorization with usage tracking';
COMMENT ON TABLE task_tags IS 'Many-to-many relationship between tasks and tags';
COMMENT ON TABLE reminders IS 'Scheduled reminders for tasks with due dates';
COMMENT ON TABLE audit_logs IS 'Immutable event log for all task operations (90-day retention)';

COMMENT ON COLUMN tasks.search_vector IS 'Generated tsvector for full-text search on title and description';
COMMENT ON COLUMN recurrence_patterns.current_occurrence IS 'Count of instances created so far (for end_condition=after_occurrences)';
COMMENT ON COLUMN tags.usage_count IS 'Number of tasks with this tag (for autocomplete ranking)';
COMMENT ON COLUMN audit_logs.correlation_id IS 'Distributed tracing correlation ID';
