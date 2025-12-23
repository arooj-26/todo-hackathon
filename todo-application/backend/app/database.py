"""Database connection and session management."""
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings


# Create engine with Neon PostgreSQL connection
# Optimized for faster connections with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Disable SQL logging for better performance
    pool_size=20,  # Keep more warm connections
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={"connect_timeout": 10}  # 10 second connection timeout
)


def get_session():
    """
    Dependency for database sessions.

    Yields a SQLModel session that automatically commits and closes.
    Used as a FastAPI dependency.
    """
    with Session(engine) as session:
        yield session


def init_db():
    """
    Initialize database tables.

    Creates all tables defined in SQLModel models.
    Should only be used in development or testing.
    In production, use Alembic migrations.
    """
    SQLModel.metadata.create_all(engine)
