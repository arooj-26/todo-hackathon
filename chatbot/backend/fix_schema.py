"""
Database schema migration script for chatbot backend.

This script fixes the user_id column type in conversations and messages tables
from VARCHAR to INTEGER to match the todo application backend.

IMPORTANT: This will DROP existing conversations and messages!
Only run this in development. In production, use proper Alembic migrations.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

print(f"🔗 Connecting to database...")
engine = create_engine(DATABASE_URL, echo=True)

def check_tables_exist():
    """Check if chatbot tables exist."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return 'conversations' in tables, 'messages' in tables

def migrate_schema():
    """Migrate schema by recreating tables with correct types."""
    with engine.connect() as conn:
        conversations_exists, messages_exists = check_tables_exist()

        print("\n📊 Current tables:")
        print(f"  - conversations: {'EXISTS' if conversations_exists else 'NOT FOUND'}")
        print(f"  - messages: {'EXISTS' if messages_exists else 'NOT FOUND'}")

        # Drop existing tables (cascades to messages)
        if conversations_exists or messages_exists:
            print("\n⚠️  WARNING: This will DELETE all existing conversations and messages!")
            response = input("Are you sure you want to continue? (yes/no): ")

            if response.lower() != 'yes':
                print("❌ Migration cancelled.")
                return

            print("\n🗑️  Dropping existing tables...")
            if messages_exists:
                conn.execute(text("DROP TABLE IF EXISTS messages CASCADE;"))
                conn.commit()
                print("  ✓ Dropped messages table")

            if conversations_exists:
                conn.execute(text("DROP TABLE IF EXISTS conversations CASCADE;"))
                conn.commit()
                print("  ✓ Dropped conversations table")

        # Create conversations table with INTEGER user_id
        print("\n📝 Creating conversations table with INTEGER user_id...")
        conn.execute(text("""
            CREATE TABLE conversations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("  ✓ Created conversations table")

        # Create index on user_id
        print("\n📊 Creating index on conversations.user_id...")
        conn.execute(text("""
            CREATE INDEX ix_conversations_user_id ON conversations(user_id);
        """))
        conn.commit()
        print("  ✓ Created index")

        # Create messages table with INTEGER user_id
        print("\n📝 Creating messages table with INTEGER user_id...")
        conn.execute(text("""
            CREATE TABLE messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("  ✓ Created messages table")

        # Create indexes on messages
        print("\n📊 Creating indexes on messages table...")
        conn.execute(text("""
            CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
        """))
        conn.execute(text("""
            CREATE INDEX ix_messages_user_id ON messages(user_id);
        """))
        conn.commit()
        print("  ✓ Created indexes")

        print("\n✅ Schema migration completed successfully!")
        print("\n📋 Summary:")
        print("  - conversations.user_id: VARCHAR → INTEGER")
        print("  - messages.user_id: VARCHAR → INTEGER")
        print("  - All conversations and messages have been cleared")

if __name__ == "__main__":
    print("=" * 60)
    print("CHATBOT BACKEND - DATABASE SCHEMA MIGRATION")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Drop existing conversations and messages tables")
    print("  2. Recreate them with INTEGER user_id columns")
    print("\n⚠️  WARNING: All existing chat data will be LOST!")
    print("=" * 60)

    try:
        migrate_schema()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
