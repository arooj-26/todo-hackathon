"""
Skill BE-002: Define API Endpoint

Creates a new FastAPI endpoint with request/response schemas and validation.
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
class DefineAPIEndpointSkill(Skill):
    """Define a new API endpoint."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="BE-002",
            name="Define API Endpoint",
            description="Create a new FastAPI endpoint with request/response schemas and validation",
            category="backend",
            version="1.0.0",
            dependencies=["BE-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "router_name": {"type": "string"},
                    "endpoint_path": {"type": "string"},
                    "http_method": {
                        "type": "string",
                        "enum": ["get", "post", "put", "patch", "delete"]
                    },
                    "request_schema": {"type": "string", "default": None},
                    "response_schema": {"type": "string"},
                    "requires_auth": {"type": "boolean", "default": True}
                },
                "required": ["router_name", "endpoint_path", "http_method", "response_schema"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "router_path": {"type": "string"},
                    "endpoint_created": {"type": "boolean"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        required = ["router_name", "endpoint_path", "http_method", "response_schema"]
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
        request_schema = params.get("request_schema")
        response_schema = params["response_schema"]
        requires_auth = params.get("requires_auth", True)

        try:
            backend_path = Path("backend")
            router_path = backend_path / "app" / "api" / "endpoints" / f"{router_name}.py"

            # Generate dependencies
            auth_dep = ""
            if requires_auth:
                auth_dep = ", current_user: User = Depends(get_current_user)"

            # Generate request parameter
            request_param = ""
            if request_schema and http_method in ["post", "put", "patch"]:
                request_param = f"data: {request_schema}, "

            # Generate function name
            func_name = endpoint_path.replace("/", "_").replace("{", "").replace("}", "").strip("_")
            if not func_name:
                func_name = http_method

            # Check if router file exists
            if router_path.exists():
                # Append to existing router
                existing_content = router_path.read_text(encoding="utf-8")

                # Generate endpoint code
                endpoint_code = f"""

@router.{http_method}("{endpoint_path}", response_model={response_schema})
async def {func_name}({request_param}db: Session = Depends(get_db){auth_dep}):
    \"\"\"
    {http_method.upper()} {endpoint_path}
    \"\"\"
    # TODO: Implement endpoint logic
    pass
"""

                # Append to router
                updated_content = existing_content + endpoint_code
                router_path.write_text(updated_content, encoding="utf-8")

            else:
                # Create new router file
                router_code = f"""from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.{router_name} import {response_schema}{"" if not request_schema else f", {request_schema}"}

router = APIRouter()


@router.{http_method}("{endpoint_path}", response_model={response_schema})
async def {func_name}({request_param}db: Session = Depends(get_db){auth_dep}):
    \"\"\"
    {http_method.upper()} {endpoint_path}
    \"\"\"
    # TODO: Implement endpoint logic
    pass
"""

                router_path.write_text(router_code, encoding="utf-8")

            self.logger.info(f"Created endpoint {http_method.upper()} {endpoint_path} in {router_path}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "router_path": str(router_path),
                    "endpoint_created": True
                },
                artifacts=[str(router_path)],
                logs=[f"Created {http_method.upper()} {endpoint_path}"]
            )

        except Exception as e:
            self.logger.exception("Failed to define API endpoint")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Endpoint function created with proper decorator",
            "Request schema validated (if applicable)",
            "Response model defined",
            "Authentication dependency added (if required)",
            "Database session dependency included",
            "Function docstring present",
            "Router registered in main.py"
        ]
