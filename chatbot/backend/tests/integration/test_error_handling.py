"""
Integration tests for FastAPI error handling.

Tests that error handlers are registered and basic endpoints work.
Full validation testing will be done in Phase 3 when chat endpoint is implemented.
"""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


class TestErrorHandling:
    """Test suite for error handling middleware and exception handlers."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_health_endpoint_success(self, client: TestClient):
        """Test that health check endpoint returns 200 with correct structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "Todo AI Chatbot API"
        assert data["version"] == "1.0.0"

    def test_root_endpoint_success(self, client: TestClient):
        """Test that root endpoint returns correct information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Todo AI Chatbot API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"

    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are properly set."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # CORS middleware should add appropriate headers
        assert "access-control-allow-origin" in response.headers

    def test_404_for_nonexistent_endpoint(self, client: TestClient):
        """Test that non-existent endpoints return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_docs_endpoint_accessible(self, client: TestClient):
        """Test that OpenAPI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client: TestClient):
        """Test that OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()

        # Verify basic OpenAPI structure
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Todo AI Chatbot API"
        assert data["info"]["version"] == "1.0.0"

    def test_exception_handlers_registered(self, client: TestClient):
        """Test that exception handlers are registered in the app."""
        from fastapi.exceptions import RequestValidationError
        from sqlalchemy.exc import SQLAlchemyError

        # Verify exception handlers are registered
        exception_handlers = app.exception_handlers

        # Should have handlers for these exception types
        assert RequestValidationError in exception_handlers
        assert SQLAlchemyError in exception_handlers
        assert Exception in exception_handlers
