from app.database import engine
from sqlmodel import text

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('Database connection: OK')

        # Check if tables exist
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = result.fetchall()
        print(f'Tables found: {[t[0] for t in tables]}')
except Exception as e:
    print(f'Database error: {e}')
