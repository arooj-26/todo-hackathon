"""
Quick test to check if tasks are being created
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Checking recent tasks...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Get all tasks for user_id = 2
cur.execute("""
    SELECT id, user_id, description, priority, completed, created_at
    FROM tasks
    WHERE user_id = 2
    ORDER BY id DESC
    LIMIT 10;
""")

print("\n📋 Tasks for user_id = 2:")
print("-" * 80)
tasks = cur.fetchall()

if not tasks:
    print("❌ No tasks found for user_id = 2")
else:
    for task in tasks:
        print(f"ID: {task[0]}")
        print(f"  Description: {task[1]}")
        print(f"  Priority: {task[3]}")
        print(f"  Completed: {task[4]}")
        print(f"  Created: {task[5]}")
        print("-" * 80)

print(f"\nTotal tasks: {len(tasks)}")

cur.close()
conn.close()
