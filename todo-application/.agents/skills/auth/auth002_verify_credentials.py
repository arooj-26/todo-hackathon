"""
Skill AUTH-002: Verify User Credentials

Verifies user email and password against database.
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
class VerifyUserCredentialsSkill(Skill):
    """Verify user credentials."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="AUTH-002",
            name="Verify User Credentials",
            description="Verify user email and password against database",
            category="auth",
            version="1.0.0",
            dependencies=["AUTH-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"},
                    "password_hash": {"type": "string"}
                },
                "required": ["email", "password", "password_hash"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "verified": {"type": "boolean"},
                    "user_email": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        required = ["email", "password", "password_hash"]
        for field in required:
            if field not in params:
                return False, f"Missing required parameter: {field}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        email = params["email"]
        password = params["password"]
        password_hash = params["password_hash"]

        try:
            from passlib.context import CryptContext

            # Initialize password context
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

            # Verify password
            verified = pwd_context.verify(password, password_hash)

            if verified:
                self.logger.info(f"Credentials verified for user: {email}")
                return SkillOutput(
                    status=SkillStatus.SUCCESS,
                    result={
                        "verified": True,
                        "user_email": email
                    },
                    logs=["Credentials verified successfully"]
                )
            else:
                self.logger.warning(f"Invalid password for user: {email}")
                return SkillOutput(
                    status=SkillStatus.SUCCESS,
                    result={
                        "verified": False,
                        "user_email": email
                    },
                    logs=["Invalid password"]
                )

        except ImportError:
            return SkillOutput(
                status=SkillStatus.FAILED,
                error="passlib not installed. Run: pip install passlib[bcrypt]"
            )
        except Exception as e:
            self.logger.exception("Failed to verify credentials")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Password compared against hash using passlib",
            "Returns True for correct password",
            "Returns False for incorrect password",
            "Constant-time comparison (via bcrypt)",
            "Email included in result",
            "No plain passwords logged"
        ]
