"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typing import Generator
from unittest.mock import patch


@pytest.fixture(name="engine")
def engine_fixture():
    """
    Create an in-memory SQLite engine for testing.
    Uses StaticPool to maintain the same connection across tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """
    Create a database session for testing.
    Automatically rolls back changes after each test.
    """
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture(autouse=True)
def reset_database(engine):
    """
    Reset database before each test.
    Ensures clean state for every test.
    """
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def patch_mcp_engine(engine):
    """
    Patch the engine in MCP tools to use the test engine.
    This allows contract tests to work with the in-memory database.
    """
    with patch('src.mcp.tools.add_task.engine', engine), \
         patch('src.mcp.tools.list_tasks.engine', engine), \
         patch('src.mcp.tools.complete_task.engine', engine), \
         patch('src.mcp.tools.delete_task.engine', engine), \
         patch('src.mcp.tools.update_task.engine', engine):
        yield
