"""
SIMPLE DATABASE FIX - No prompts, just fixes the schema
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("🔧 Fixing database schema...")
print("This will:")
print("  1. Drop old conversations and messages tables")
print("  2. Recreate with INTEGER user_id")
print("")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # Drop old tables
    print("🗑️  Dropping old tables...")
    cur.execute("DROP TABLE IF EXISTS messages CASCADE;")
    cur.execute("DROP TABLE IF EXISTS conversations CASCADE;")
    conn.commit()
    print("✓ Dropped tables")

    # Create conversations with INTEGER user_id
    print("📝 Creating conversations table...")
    cur.execute("""
        CREATE TABLE conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("CREATE INDEX ix_conversations_user_id ON conversations(user_id);")
    conn.commit()
    print("✓ Created conversations table")

    # Create messages with INTEGER user_id
    print("📝 Creating messages table...")
    cur.execute("""
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);")
    cur.execute("CREATE INDEX ix_messages_user_id ON messages(user_id);")
    conn.commit()
    print("✓ Created messages table")

    print("")
    print("✅ SUCCESS! Database schema fixed!")
    print("")
    print("Next steps:")
    print("  1. Restart chatbot backend: uvicorn src.api.main:app --reload --port 8001")
    print("  2. Clear browser localStorage (F12 → Application → Local Storage → delete 'chatbot_conversation_id')")
    print("  3. Refresh dashboard and try chatbot again!")

except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
