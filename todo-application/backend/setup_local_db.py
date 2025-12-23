"""
Script to set up local PostgreSQL database for the Todo application.
This creates the database and all tables using your existing models.
"""
import sys
import psycopg
from psycopg import sql
from sqlmodel import SQLModel, create_engine
from app.models.user import User
from app.models.task import Task

# Database connection parameters
DB_USER = "postgres"
DB_PASSWORD = "postgress123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "tododb"

def create_database():
    """Create the database if it doesn't exist."""
    # Connect to PostgreSQL server (default 'postgres' database)
    try:
        print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}...")
        conn = psycopg.connect(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres",
            autocommit=True
        )
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()

        if exists:
            print(f"[OK] Database '{DB_NAME}' already exists")
        else:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
            )
            print(f"[OK] Database '{DB_NAME}' created successfully")

        cursor.close()
        conn.close()
        return True

    except psycopg.OperationalError as e:
        print(f"[ERROR] Cannot connect to PostgreSQL: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. PostgreSQL service is started")
        print(f"3. Username '{DB_USER}' and password are correct")
        print(f"4. PostgreSQL is listening on {DB_HOST}:{DB_PORT}")
        print("\nTo start PostgreSQL service:")
        print("  - Windows: Services -> postgresql-x64-XX -> Start")
        print("  - Or use: pg_ctl -D \"C:\\Program Files\\PostgreSQL\\XX\\data\" start")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def create_tables():
    """Create all tables using SQLModel."""
    try:
        print(f"\nConnecting to database '{DB_NAME}'...")
        database_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(database_url, echo=False)

        print("Creating tables from your models...")
        SQLModel.metadata.create_all(engine)
        print("[OK] All tables created successfully")

        # Display created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if tables:
            print(f"\nCreated tables:")
            for table in tables:
                columns = inspector.get_columns(table)
                print(f"  - {table} ({len(columns)} columns)")
        else:
            print("\nNo tables were created (they may already exist)")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 70)
    print("Todo Application - Local PostgreSQL Setup")
    print("=" * 70)
    print("\nThis will create a local database for fast development.")
    print("Your Neon database will remain unchanged.\n")
    print("-" * 70)

    # Step 1: Create database
    if not create_database():
        print("\n" + "=" * 70)
        print("[FAILED] Database setup failed")
        print("=" * 70)
        sys.exit(1)

    # Step 2: Create tables
    if not create_tables():
        print("\n" + "=" * 70)
        print("[FAILED] Table creation failed")
        print("=" * 70)
        sys.exit(1)

    print("\n" + "=" * 70)
    print("[SUCCESS] Local database setup completed!")
    print("=" * 70)
    print(f"\nLocal Database Configuration:")
    print(f"  Database: {DB_NAME}")
    print(f"  Host: {DB_HOST}:{DB_PORT}")
    print(f"  User: {DB_USER}")
    print(f"\nConnection String:")
    print(f"  postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
