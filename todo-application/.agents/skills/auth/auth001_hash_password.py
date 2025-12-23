"""
Skill AUTH-001: Hash Password

Hashes passwords using bcrypt for secure storage.
"""

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
class HashPasswordSkill(Skill):
    """Hash passwords with bcrypt."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="AUTH-001",
            name="Hash Password",
            description="Hash passwords using bcrypt for secure storage",
            category="auth",
            version="1.0.0",
            dependencies=[],
            inputs_schema={
                "type": "object",
                "properties": {
                    "password": {"type": "string", "minLength": 8}
                },
                "required": ["password"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "password_hash": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        if "password" not in params:
            return False, "Missing required parameter: password"

        password = params["password"]
        if not isinstance(password, str):
            return False, "Password must be a string"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        password = params["password"]

        try:
            from passlib.context import CryptContext

            # Initialize password context
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

            # Hash the password
            password_hash = pwd_context.hash(password)

            self.logger.info("Password hashed successfully")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={"password_hash": password_hash},
                logs=["Password hashed with bcrypt"]
            )

        except ImportError:
            return SkillOutput(
                status=SkillStatus.FAILED,
                error="passlib not installed. Run: pip install passlib[bcrypt]"
            )
        except Exception as e:
            self.logger.exception("Failed to hash password")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Password hashed using bcrypt",
            "Hash is different from plain password",
            "Hash length is appropriate for bcrypt",
            "Same password produces different hashes (salted)",
            "passlib library used for hashing"
        ]
