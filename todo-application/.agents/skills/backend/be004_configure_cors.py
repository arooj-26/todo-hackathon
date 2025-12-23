"""
Skill BE-004: Configure CORS

Configures Cross-Origin Resource Sharing (CORS) middleware for FastAPI.
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
class ConfigureCORSSkill(Skill):
    """Configure CORS middleware."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="BE-004",
            name="Configure CORS",
            description="Configure Cross-Origin Resource Sharing (CORS) middleware for FastAPI",
            category="backend",
            version="1.0.0",
            dependencies=["BE-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "allowed_origins": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["http://localhost:3000"]
                    },
                    "allow_credentials": {"type": "boolean", "default": True},
                    "allow_methods": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["*"]
                    },
                    "allow_headers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["*"]
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "cors_configured": {"type": "boolean"},
                    "main_py_updated": {"type": "boolean"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        main_py_path = backend_path / "app" / "main.py"
        if not main_py_path.exists():
            return False, "main.py does not exist. Run BE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        allowed_origins = params.get("allowed_origins", ["http://localhost:3000"])
        allow_credentials = params.get("allow_credentials", True)
        allow_methods = params.get("allow_methods", ["*"])
        allow_headers = params.get("allow_headers", ["*"])

        try:
            backend_path = Path("backend")
            main_py_path = backend_path / "app" / "main.py"

            # Read existing main.py
            main_py_content = main_py_path.read_text(encoding="utf-8")

            # Check if CORS is already configured
            if "CORSMiddleware" in main_py_content and "add_middleware" in main_py_content:
                self.logger.info("CORS already configured in main.py")

                return SkillOutput(
                    status=SkillStatus.SUCCESS,
                    result={
                        "cors_configured": True,
                        "main_py_updated": False
                    },
                    artifacts=[str(main_py_path)],
                    logs=["CORS already configured"]
                )

            # Add CORS import if not present
            if "from fastapi.middleware.cors import CORSMiddleware" not in main_py_content:
                # Add import after FastAPI import
                main_py_content = main_py_content.replace(
                    "from fastapi import FastAPI",
                    "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware"
                )

            # Add CORS middleware configuration
            cors_config = f"""
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins={allowed_origins},
    allow_credentials={allow_credentials},
    allow_methods={allow_methods},
    allow_headers={allow_headers},
)
"""

            # Insert CORS configuration after app creation
            if "app = FastAPI(" in main_py_content:
                # Find the end of FastAPI initialization
                lines = main_py_content.split("\n")
                insert_index = -1
                brace_count = 0
                found_app = False

                for i, line in enumerate(lines):
                    if "app = FastAPI(" in line:
                        found_app = True
                        brace_count += line.count("(") - line.count(")")

                    elif found_app:
                        brace_count += line.count("(") - line.count(")")

                        if brace_count == 0:
                            insert_index = i + 1
                            break

                if insert_index > 0:
                    lines.insert(insert_index, cors_config)
                    main_py_content = "\n".join(lines)

            # Write updated main.py
            main_py_path.write_text(main_py_content, encoding="utf-8")

            self.logger.info("Configured CORS in main.py")

            # Update config.py to include ALLOWED_ORIGINS
            config_py_path = backend_path / "app" / "core" / "config.py"
            if config_py_path.exists():
                config_content = config_py_path.read_text(encoding="utf-8")

                if "ALLOWED_ORIGINS" not in config_content:
                    # Add ALLOWED_ORIGINS to Settings class
                    config_content = config_content.replace(
                        "class Settings(BaseSettings):",
                        f'class Settings(BaseSettings):\n    # CORS\n    ALLOWED_ORIGINS: List[str] = {allowed_origins}'
                    )

                    # Ensure List import
                    if "from typing import List" not in config_content:
                        config_content = "from typing import List\n" + config_content

                    config_py_path.write_text(config_content, encoding="utf-8")
                    self.logger.info("Updated config.py with ALLOWED_ORIGINS")

            artifacts = [str(main_py_path), str(config_py_path)]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "cors_configured": True,
                    "main_py_updated": True
                },
                artifacts=artifacts,
                logs=["Configured CORS middleware", f"Allowed origins: {allowed_origins}"]
            )

        except Exception as e:
            self.logger.exception("Failed to configure CORS")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "CORSMiddleware imported in main.py",
            "CORS middleware added to FastAPI app",
            "Allowed origins configured",
            "Credentials allowed (if required)",
            "All HTTP methods allowed (or specific methods)",
            "All headers allowed (or specific headers)",
            "ALLOWED_ORIGINS in config.py",
            "No CORS errors when frontend connects"
        ]
