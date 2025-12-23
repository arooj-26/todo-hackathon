-- Migration: 001 - Initial Schema
-- Date: 2025-12-21
-- Description: Create initial database schema for todo chatbot

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high');
CREATE TYPE role_enum AS ENUM ('user', 'assistant');

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index for querying user conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
    ON conversations(user_id, updated_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role role_enum NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for querying messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
    ON messages(conversation_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_messages_user_conversation
    ON messages(user_id, conversation_id);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    priority priority_enum NOT NULL DEFAULT 'medium'
);

-- Create indexes for querying tasks
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed
    ON tasks(user_id, completed);

CREATE INDEX IF NOT EXISTS idx_tasks_user_priority
    ON tasks(user_id, priority);

CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date
    ON tasks(user_id, due_date);

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Chat sessions between users and AI assistant';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON TABLE tasks IS 'User todo tasks';

COMMENT ON COLUMN tasks.completed IS 'Whether the task has been completed';
COMMENT ON COLUMN tasks.priority IS 'Task priority level (low, medium, high)';
COMMENT ON COLUMN messages.role IS 'Message author (user or assistant)';
