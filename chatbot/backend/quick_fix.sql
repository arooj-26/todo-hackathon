-- Quick fix for chatbot database schema
-- This fixes the user_id type mismatch issue

-- Step 1: Drop old tables (this will delete chat history)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;

-- Step 2: Create conversations table with INTEGER user_id
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_conversations_user_id ON conversations(user_id);

-- Step 3: Create messages table with INTEGER user_id
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
CREATE INDEX ix_messages_user_id ON messages(user_id);

-- Done! Now conversations.user_id and messages.user_id are INTEGER
