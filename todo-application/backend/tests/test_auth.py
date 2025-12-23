"""Integration tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import User


def test_signup_success(client: TestClient, session: Session):
    """
    Test T037: Signup flow - create account → receive token → redirect to dashboard
    """
    # Create new account
    response = client.post(
        "/auth/signup",
        json={"email": "newuser@example.com", "password": "securepass123"}
    )

    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

    # Verify user data
    user = data["user"]
    assert user["email"] == "newuser@example.com"
    assert "id" in user
    assert "created_at" in user
    assert "password_hash" not in user  # Should not expose password

    # Verify token can be used to access protected endpoint
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "newuser@example.com"


def test_signup_duplicate_email(client: TestClient, session: Session):
    """Test signup with duplicate email returns 409 Conflict."""
    # Create first user
    client.post(
        "/auth/signup",
        json={"email": "duplicate@example.com", "password": "password123"}
    )

    # Try to create another user with same email
    response = client.post(
        "/auth/signup",
        json={"email": "duplicate@example.com", "password": "different123"}
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_signin_success(client: TestClient, session: Session):
    """
    Test T038: Signin flow - valid credentials → receive token → access dashboard
    """
    # Create user first
    signup_response = client.post(
        "/auth/signup",
        json={"email": "signin@example.com", "password": "password123"}
    )
    assert signup_response.status_code == 201
    user_id = signup_response.json()["user"]["id"]

    # Sign in with valid credentials
    response = client.post(
        "/auth/signin",
        json={"email": "signin@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["id"] == user_id
    assert data["user"]["email"] == "signin@example.com"

    # Verify token can be used to access protected endpoint
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200


def test_signin_invalid_email(client: TestClient, session: Session):
    """Test signin with non-existent email returns 401."""
    response = client.post(
        "/auth/signin",
        json={"email": "nonexistent@example.com", "password": "password123"}
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_signin_invalid_password(client: TestClient, session: Session):
    """Test signin with wrong password returns 401."""
    # Create user
    client.post(
        "/auth/signup",
        json={"email": "wrongpass@example.com", "password": "correctpass123"}
    )

    # Try to sign in with wrong password
    response = client.post(
        "/auth/signin",
        json={"email": "wrongpass@example.com", "password": "wrongpass123"}
    )

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_signout_success(client: TestClient, session: Session):
    """
    Test T039: Signout flow - clear token → redirect to signin
    """
    # Create user and get token
    signup_response = client.post(
        "/auth/signup",
        json={"email": "signout@example.com", "password": "password123"}
    )
    token = signup_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify token works before signout
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200

    # Sign out
    signout_response = client.post("/auth/signout", headers=headers)
    assert signout_response.status_code == 204

    # Note: In a stateless JWT setup, the token is still valid on the server
    # Client is responsible for removing the token from storage
    # Token revocation would require additional server-side logic


def test_protected_route_without_token(client: TestClient, session: Session):
    """
    Test T040: Protected routes - no token → 401 → redirect to signin
    """
    # Try to access protected endpoint without token
    response = client.get("/auth/me")

    assert response.status_code == 403  # FastAPI returns 403 for missing auth


def test_protected_route_invalid_token(client: TestClient, session: Session):
    """Test protected route with invalid token returns 401."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_protected_route_expired_token(client: TestClient, session: Session):
    """Test protected route with malformed token returns 401."""
    # Token with invalid structure
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401


def test_get_current_user_info(client: TestClient, session: Session):
    """Test GET /auth/me returns current user info."""
    # Create user and get token
    signup_response = client.post(
        "/auth/signup",
        json={"email": "me@example.com", "password": "password123"}
    )
    token = signup_response.json()["access_token"]
    user_id = signup_response.json()["user"]["id"]

    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "me@example.com"
    assert "password_hash" not in data
