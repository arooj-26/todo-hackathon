"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a fresh in-memory database for each test.

    This fixture provides an isolated database session for testing.
    Uses SQLite in-memory database for fast test execution.

    Yields:
        Session: SQLModel database session
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a FastAPI test client with database dependency override.

    This fixture provides a test client that uses the test database
    session instead of the production database.

    Args:
        session: Test database session from session_fixture

    Yields:
        TestClient: FastAPI test client
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
