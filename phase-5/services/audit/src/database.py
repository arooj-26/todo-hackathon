"""Database configuration for Audit Service."""

import os
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


class DatabaseManager:
    """Database connection manager for Audit Service."""

    def __init__(self):
        """Initialize database manager."""
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@postgres:5432/todo_chatbot"
        )

        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        self.async_session_maker = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self):
        """Create database tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        """Get database session.
        
        Returns:
            AsyncSession: Database session
        """
        async with self.async_session_maker() as session:
            yield session

    async def close(self):
        """Close database engine."""
        await self.engine.dispose()


# Global database manager instance
db_manager: DatabaseManager | None = None


async def get_db() -> AsyncSession:
    """FastAPI dependency for database session."""
    global db_manager
    if not db_manager:
        db_manager = DatabaseManager()
    
    async for session in db_manager.get_session():
        yield session
