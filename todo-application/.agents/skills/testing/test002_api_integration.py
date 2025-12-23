"""
Skill TEST-002: Write API Integration Test

Creates pytest integration tests for FastAPI endpoints using TestClient.
"""

from pathlib import Path
from typing import List
from ...lib.skill_base import (
    Skill,
    SkillMetadata,
    SkillInput,
    SkillOutput,
    SkillStatus,
    register_skill
)


@register_skill
class WriteAPIIntegrationTestSkill(Skill):
    """Write integration tests for API endpoints."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="TEST-002",
            name="Write API Integration Test",
            description="Create pytest integration tests for FastAPI endpoints using TestClient",
            category="testing",
            version="1.0.0",
            dependencies=["BE-001", "BE-002"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "router_name": {"type": "string"},
                    "endpoint_path": {"type": "string"},
                    "http_method": {"type": "string"},
                    "test_scenarios": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["success response", "authentication required", "validation error"]
                    }
                },
                "required": ["router_name", "endpoint_path", "http_method"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "test_file_path": {"type": "string"},
                    "scenarios_count": {"type": "integer"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        required = ["router_name", "endpoint_path", "http_method"]
        for field in required:
            if field not in params:
                return False, f"Missing required parameter: {field}"

        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        router_name = params["router_name"]
        endpoint_path = params["endpoint_path"]
        http_method = params["http_method"].lower()
        test_scenarios = params.get("test_scenarios", ["success response", "authentication required", "validation error"])

        try:
            backend_path = Path("backend")
            test_dir = backend_path / "tests"
            test_file_path = test_dir / f"test_{router_name}_api.py"

            # Generate test imports
            test_imports = """import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
"""

            # Generate test cases
            test_cases = []

            # Create fixtures if needed
            fixtures = """
@pytest.fixture
def auth_headers(test_user_token):
    \"\"\"Get authentication headers.\"\"\"
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def test_user_token():
    \"\"\"Create a test user and return auth token.\"\"\"
    # Create test user
    response = client.post(
        "/api/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    return response.json()["access_token"]
"""

            for scenario in test_scenarios:
                scenario_lower = scenario.lower()

                if "success" in scenario_lower:
                    test_cases.append(f"""
def test_{router_name}_{http_method}_success(auth_headers):
    \"\"\"Test {http_method.upper()} {endpoint_path} returns success.\"\"\"
    response = client.{http_method}(
        "{endpoint_path}",
        headers=auth_headers
    )
    assert response.status_code == 200
    # TODO: Add response body assertions
""")

                elif "auth" in scenario_lower or "unauthorized" in scenario_lower:
                    test_cases.append(f"""
def test_{router_name}_{http_method}_requires_auth():
    \"\"\"Test {http_method.upper()} {endpoint_path} requires authentication.\"\"\"
    response = client.{http_method}("{endpoint_path}")
    assert response.status_code == 401
    assert "detail" in response.json()
""")

                elif "validation" in scenario_lower or "invalid" in scenario_lower:
                    test_cases.append(f"""
def test_{router_name}_{http_method}_validation_error(auth_headers):
    \"\"\"Test {http_method.upper()} {endpoint_path} with invalid data.\"\"\"
    response = client.{http_method}(
        "{endpoint_path}",
        headers=auth_headers,
        json={{}}  # Invalid/missing data
    )
    assert response.status_code == 422
    assert "detail" in response.json()
""")

                elif "404" in scenario_lower or "not found" in scenario_lower:
                    test_cases.append(f"""
def test_{router_name}_{http_method}_not_found(auth_headers):
    \"\"\"Test {http_method.upper()} {endpoint_path} with non-existent resource.\"\"\"
    response = client.{http_method}(
        "{endpoint_path.replace('{id}', '99999')}",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "detail" in response.json()
""")

                elif "403" in scenario_lower or "forbidden" in scenario_lower:
                    test_cases.append(f"""
def test_{router_name}_{http_method}_forbidden(auth_headers):
    \"\"\"Test {http_method.upper()} {endpoint_path} with insufficient permissions.\"\"\"
    # Try to access another user's resource
    response = client.{http_method}(
        "{endpoint_path}",
        headers=auth_headers
    )
    assert response.status_code == 403
    assert "detail" in response.json()
""")

            test_code = test_imports + fixtures + "\n".join(test_cases)

            # Write or append to test file
            if test_file_path.exists():
                existing_content = test_file_path.read_text(encoding="utf-8")
                test_code = existing_content + "\n\n" + "\n".join(test_cases)

            test_file_path.write_text(test_code, encoding="utf-8")

            self.logger.info(f"Created API integration test: {test_file_path}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "test_file_path": str(test_file_path),
                    "scenarios_count": len(test_cases)
                },
                artifacts=[str(test_file_path)],
                logs=[f"Created {len(test_cases)} integration test scenarios"]
            )

        except Exception as e:
            self.logger.exception("Failed to create API integration test")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "TestClient imported and configured",
            "Test functions use client.get/post/put/delete",
            "Authentication tests included",
            "Status code assertions present",
            "Response body validation included",
            "Test fixtures for auth tokens",
            "Error scenarios covered (401, 403, 404, 422)"
        ]
