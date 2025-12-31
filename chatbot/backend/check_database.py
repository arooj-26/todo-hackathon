"""
Diagnostic script to check what's in the database
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 60)
print("DATABASE DIAGNOSTIC")
print("=" * 60)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # Check conversations table schema
    print("\n1️⃣ CONVERSATIONS TABLE SCHEMA:")
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'conversations'
        ORDER BY ordinal_position;
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")

    # Check messages table schema
    print("\n2️⃣ MESSAGES TABLE SCHEMA:")
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'messages'
        ORDER BY ordinal_position;
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")

    # Check tasks table schema
    print("\n3️⃣ TASKS TABLE SCHEMA:")
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'tasks'
        ORDER BY ordinal_position;
    """)
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")

    # Count conversations
    print("\n4️⃣ CONVERSATIONS COUNT:")
    cur.execute("SELECT COUNT(*) FROM conversations;")
    count = cur.fetchone()[0]
    print(f"   Total conversations: {count}")

    if count > 0:
        cur.execute("SELECT id, user_id, created_at FROM conversations ORDER BY id DESC LIMIT 5;")
        print("\n   Recent conversations:")
        for row in cur.fetchall():
            print(f"   - ID: {row[0]}, User ID: {row[1]} (type: {type(row[1])}), Created: {row[2]}")

    # Count messages
    print("\n5️⃣ MESSAGES COUNT:")
    cur.execute("SELECT COUNT(*) FROM messages;")
    count = cur.fetchone()[0]
    print(f"   Total messages: {count}")

    if count > 0:
        cur.execute("SELECT id, user_id, role, LEFT(content, 50) FROM messages ORDER BY id DESC LIMIT 5;")
        print("\n   Recent messages:")
        for row in cur.fetchall():
            print(f"   - ID: {row[0]}, User ID: {row[1]} (type: {type(row[1])}), Role: {row[2]}, Content: {row[3]}...")

    # Count tasks
    print("\n6️⃣ TASKS COUNT:")
    cur.execute("SELECT COUNT(*) FROM tasks;")
    count = cur.fetchone()[0]
    print(f"   Total tasks: {count}")

    if count > 0:
        cur.execute("SELECT id, user_id, description, completed FROM tasks ORDER BY id DESC LIMIT 10;")
        print("\n   Recent tasks:")
        for row in cur.fetchall():
            print(f"   - ID: {row[0]}, User ID: {row[1]} (type: {type(row[1])}), Description: {row[2]}, Completed: {row[3]}")

    # Check for user_id type mismatch
    print("\n7️⃣ TYPE MISMATCH CHECK:")

    # Check conversations.user_id type
    cur.execute("""
        SELECT data_type
        FROM information_schema.columns
        WHERE table_name = 'conversations' AND column_name = 'user_id';
    """)
    conv_type = cur.fetchone()[0]

    # Check tasks.user_id type
    cur.execute("""
        SELECT data_type
        FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'user_id';
    """)
    task_type = cur.fetchone()[0]

    print(f"   conversations.user_id: {conv_type}")
    print(f"   tasks.user_id: {task_type}")

    if conv_type != task_type:
        print(f"   ⚠️  TYPE MISMATCH! This will cause issues!")
    else:
        print(f"   ✓ Types match")

    print("\n" + "=" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
