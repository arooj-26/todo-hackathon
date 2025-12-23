"""
Database connection and session management.

Provides SQLModel engine and FastAPI dependency for database sessions.
"""
from sqlmodel import Session, create_engine
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if we're in a test environment (pytest sets this during test runs)
IS_TESTING = "PYTEST_CURRENT_TEST" in os.environ

# Only require DATABASE_URL in non-test environments
if not DATABASE_URL and not IS_TESTING:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure it in your .env file."
    )

# Create engine with connection pooling (only if DATABASE_URL is set)
# In test environments, tests will provide their own engine fixtures
engine = None
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging (development only)
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Maximum additional connections when pool is exhausted
    )


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Provides a database session that automatically commits on success
    and rolls back on exceptions.

    Yields:
        Session: SQLModel database session

    Example:
        ```python
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            tasks = session.query(Task).all()
            return tasks
        ```
    """
    with Session(engine) as session:
        yield session
