"""Database connection manager with Neon PostgreSQL configuration."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


class DatabaseManager:
    """Manager for PostgreSQL database connections.

    Supports Neon Serverless PostgreSQL with connection pooling and
    async operations via SQLAlchemy.
    """

    def __init__(self):
        """Initialize database manager."""
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        # Convert postgresql:// to postgresql+asyncpg:// for async support
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Create async engine
        self.engine = create_async_engine(
            database_url,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_pre_ping=True,  # Test connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour (important for Neon)
        )

        # Create session factory
        self.async_session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self):
        """Create all tables (for development/testing only).

        Production deployments should use Alembic migrations.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def close(self):
        """Close database connections."""
        await self.engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session.

        Yields:
            AsyncSession: Database session

        Example:
            async with db_manager.get_session() as session:
                result = await session.execute(select(Task))
                tasks = result.scalars().all()
        """
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance.

    Returns:
        DatabaseManager: Initialized manager

    Raises:
        RuntimeError: If manager not initialized
    """
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/tasks")
        async def get_tasks(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Task))
            return result.scalars().all()
    """
    manager = get_db_manager()
    async with manager.get_session() as session:
        yield session
