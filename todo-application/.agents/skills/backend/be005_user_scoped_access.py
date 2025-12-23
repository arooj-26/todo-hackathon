"""
Skill BE-005: Implement User-Scoped Data Access

Implements helper functions and dependencies for user-scoped data access patterns.
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
class ImplementUserScopedAccessSkill(Skill):
    """Implement user-scoped data access patterns."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="BE-005",
            name="Implement User-Scoped Data Access",
            description="Implement helper functions and dependencies for user-scoped data access",
            category="backend",
            version="1.0.0",
            dependencies=["BE-001", "BE-003"],
            inputs_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "helpers_path": {"type": "string"},
                    "middleware_path": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        try:
            backend_path = Path("backend")
            core_path = backend_path / "app" / "core"

            # Create user_scoped.py helper module
            helpers_path = core_path / "user_scoped.py"
            helpers_code = """from typing import Optional
from fastapi import HTTPException, Path as PathParam, status
from sqlmodel import Session, select
from app.models.user import User


def verify_user_access(
    user_id: int,
    current_user: User,
    allow_admin_override: bool = False
) -> None:
    \"\"\"
    Verify that the current user has access to resources for the given user_id.

    Args:
        user_id: The user ID being accessed
        current_user: The authenticated user making the request
        allow_admin_override: If True, admin users can access any user's data

    Raises:
        HTTPException: If user does not have access
    \"\"\"
    if current_user.id != user_id:
        if allow_admin_override and getattr(current_user, 'is_admin', False):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )


def get_user_id_from_path(user_id: int = PathParam(..., description="User ID")) -> int:
    \"\"\"
    Extract and validate user_id from path parameter.

    Args:
        user_id: User ID from path

    Returns:
        Validated user ID

    Raises:
        HTTPException: If user_id is invalid
    \"\"\"
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    return user_id


def filter_by_user_id(statement, model, user_id: int):
    \"\"\"
    Add user_id filter to a SQLModel select statement.

    Args:
        statement: SQLModel select statement
        model: The model class
        user_id: User ID to filter by

    Returns:
        Filtered select statement
    \"\"\"
    return statement.where(model.user_id == user_id)


def verify_resource_ownership(
    resource,
    current_user: User,
    resource_name: str = "resource"
) -> None:
    \"\"\"
    Verify that a resource belongs to the current user.

    Args:
        resource: The resource object (must have user_id attribute)
        current_user: The authenticated user
        resource_name: Name of the resource for error message

    Raises:
        HTTPException: If resource doesn't belong to user
    \"\"\"
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name.capitalize()} not found"
        )

    if not hasattr(resource, 'user_id'):
        raise ValueError(f"Resource {resource_name} does not have user_id attribute")

    if resource.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to access this {resource_name}"
        )


class UserScopedQuery:
    \"\"\"Helper class for user-scoped database queries.\"\"\"

    def __init__(self, db: Session, user: User):
        \"\"\"
        Initialize user-scoped query helper.

        Args:
            db: Database session
            user: Current authenticated user
        \"\"\"
        self.db = db
        self.user = user

    def get_all(self, model):
        \"\"\"Get all records for the current user.\"\"\"
        statement = select(model).where(model.user_id == self.user.id)
        return self.db.exec(statement).all()

    def get_by_id(self, model, resource_id: int):
        \"\"\"
        Get a specific record by ID for the current user.

        Args:
            model: SQLModel class
            resource_id: Resource ID

        Returns:
            Resource object or None
        \"\"\"
        statement = select(model).where(
            model.id == resource_id,
            model.user_id == self.user.id
        )
        return self.db.exec(statement).first()

    def get_or_404(self, model, resource_id: int, resource_name: str = "resource"):
        \"\"\"
        Get a record or raise 404 if not found or not owned by user.

        Args:
            model: SQLModel class
            resource_id: Resource ID
            resource_name: Name for error messages

        Returns:
            Resource object

        Raises:
            HTTPException: If resource not found or not authorized
        \"\"\"
        resource = self.get_by_id(model, resource_id)

        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{resource_name.capitalize()} not found"
            )

        return resource

    def create(self, resource):
        \"\"\"
        Create a new resource for the current user.

        Args:
            resource: Resource object to create (will set user_id)

        Returns:
            Created resource
        \"\"\"
        if hasattr(resource, 'user_id'):
            resource.user_id = self.user.id

        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)

        return resource

    def update(self, resource):
        \"\"\"
        Update a resource (verifies ownership).

        Args:
            resource: Resource object to update

        Returns:
            Updated resource
        \"\"\"
        verify_resource_ownership(resource, self.user)

        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)

        return resource

    def delete(self, resource):
        \"\"\"
        Delete a resource (verifies ownership).

        Args:
            resource: Resource object to delete
        \"\"\"
        verify_resource_ownership(resource, self.user)

        self.db.delete(resource)
        self.db.commit()
"""

            helpers_path.write_text(helpers_code, encoding="utf-8")
            self.logger.info(f"Created user-scoped helpers: {helpers_path}")

            # Create middleware for user_id validation
            middleware_path = core_path / "user_middleware.py"
            middleware_code = """from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class UserIDValidationMiddleware(BaseHTTPMiddleware):
    \"\"\"
    Middleware to validate user_id in path matches authenticated user.

    For routes with {user_id} path parameter, ensures the authenticated user
    can only access their own resources.
    \"\"\"

    async def dispatch(self, request: Request, call_next):
        \"\"\"Process request and validate user_id if present.\"\"\"
        # Check if path contains user_id parameter
        if "{user_id}" in str(request.url.path) or "user_id" in request.path_params:
            # Get user_id from path
            path_user_id = request.path_params.get("user_id")

            if path_user_id:
                try:
                    path_user_id = int(path_user_id)

                    # Get authenticated user from request state (set by auth dependency)
                    authenticated_user = getattr(request.state, "user", None)

                    if authenticated_user and authenticated_user.id != path_user_id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Cannot access another user's resources"
                        )

                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid user_id format"
                    )

        response = await call_next(request)
        return response
"""

            middleware_path.write_text(middleware_code, encoding="utf-8")
            self.logger.info(f"Created user middleware: {middleware_path}")

            artifacts = [str(helpers_path), str(middleware_path)]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "helpers_path": str(helpers_path),
                    "middleware_path": str(middleware_path)
                },
                artifacts=artifacts,
                logs=[f"Created user-scoped access with {len(artifacts)} files"]
            )

        except Exception as e:
            self.logger.exception("Failed to implement user-scoped access")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "verify_user_access function validates user ownership",
            "filter_by_user_id adds user_id filter to queries",
            "verify_resource_ownership checks resource ownership",
            "UserScopedQuery helper class for CRUD operations",
            "All queries filtered by current user's ID",
            "403 Forbidden raised for unauthorized access",
            "Middleware validates user_id in path parameters",
            "Resources automatically scoped to creating user"
        ]
