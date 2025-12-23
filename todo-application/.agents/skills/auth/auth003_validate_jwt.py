"""
Skill AUTH-003: Validate JWT Token

Validates and decodes JWT access tokens.
"""

from typing import List, Optional
from ...lib.skill_base import (
    Skill,
    SkillMetadata,
    SkillInput,
    SkillOutput,
    SkillStatus,
    register_skill
)


@register_skill
class ValidateJWTTokenSkill(Skill):
    """Validate JWT tokens."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="AUTH-003",
            name="Validate JWT Token",
            description="Validate and decode JWT access tokens",
            category="auth",
            version="1.0.0",
            dependencies=[],
            inputs_schema={
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "secret_key": {"type": "string"},
                    "algorithm": {"type": "string", "default": "HS256"}
                },
                "required": ["token", "secret_key"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "payload": {"type": "object"},
                    "error": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        required = ["token", "secret_key"]
        for field in required:
            if field not in params:
                return False, f"Missing required parameter: {field}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        token = params["token"]
        secret_key = params["secret_key"]
        algorithm = params.get("algorithm", "HS256")

        try:
            from jose import jwt, JWTError

            # Decode and validate token
            try:
                payload = jwt.decode(token, secret_key, algorithms=[algorithm])

                # Check expiration
                from datetime import datetime
                exp = payload.get("exp")
                if exp:
                    exp_datetime = datetime.fromtimestamp(exp)
                    if exp_datetime < datetime.utcnow():
                        self.logger.warning("Token has expired")
                        return SkillOutput(
                            status=SkillStatus.SUCCESS,
                            result={
                                "valid": False,
                                "payload": None,
                                "error": "Token has expired"
                            },
                            logs=["Token expired"]
                        )

                self.logger.info("Token validated successfully")

                return SkillOutput(
                    status=SkillStatus.SUCCESS,
                    result={
                        "valid": True,
                        "payload": payload,
                        "error": None
                    },
                    logs=["Token validated successfully"]
                )

            except JWTError as e:
                self.logger.warning(f"Invalid token: {str(e)}")
                return SkillOutput(
                    status=SkillStatus.SUCCESS,
                    result={
                        "valid": False,
                        "payload": None,
                        "error": f"Invalid token: {str(e)}"
                    },
                    logs=[f"Token validation failed: {str(e)}"]
                )

        except ImportError:
            return SkillOutput(
                status=SkillStatus.FAILED,
                error="python-jose not installed. Run: pip install python-jose[cryptography]"
            )
        except Exception as e:
            self.logger.exception("Failed to validate JWT token")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Token decoded using python-jose",
            "Signature verified with secret key",
            "Expiration time checked",
            "Returns valid=True for valid tokens",
            "Returns valid=False for invalid/expired tokens",
            "Payload extracted from valid tokens",
            "Clear error messages for failures"
        ]
