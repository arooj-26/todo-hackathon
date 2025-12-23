"""
Skill FE-001: Initialize Next.js Project

Creates a new Next.js 16+ application with App Router and TypeScript configuration.
"""

import subprocess
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
class InitNextJsProjectSkill(Skill):
    """Initialize a new Next.js project."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="FE-001",
            name="Initialize Next.js Project",
            description="Create a new Next.js 16+ application with App Router and TypeScript",
            category="frontend",
            version="1.0.0",
            dependencies=[],
            inputs_schema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string"},
                    "use_typescript": {"type": "boolean", "default": True},
                    "use_tailwind": {"type": "boolean", "default": True},
                    "use_app_router": {"type": "boolean", "default": True}
                },
                "required": ["project_name"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "package_json_path": {"type": "string"},
                    "tsconfig_path": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        # Check required parameters
        if "project_name" not in params:
            return False, "Missing required parameter: project_name"

        project_name = params["project_name"]
        if not isinstance(project_name, str) or not project_name:
            return False, "project_name must be a non-empty string"

        # Check if directory already exists
        project_path = Path("frontend")
        if project_path.exists():
            return False, f"Directory already exists: {project_path}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        project_name = params["project_name"]
        use_typescript = params.get("use_typescript", True)
        use_tailwind = params.get("use_tailwind", True)
        use_app_router = params.get("use_app_router", True)

        try:
            # Build create-next-app command
            cmd = [
                "npx",
                "create-next-app@latest",
                "frontend",
                "--no-git"  # Don't initialize git (already in repo)
            ]

            if use_typescript:
                cmd.append("--typescript")
            else:
                cmd.append("--javascript")

            if use_tailwind:
                cmd.append("--tailwind")
            else:
                cmd.append("--no-tailwind")

            if use_app_router:
                cmd.append("--app")
            else:
                cmd.append("--pages")

            cmd.extend([
                "--no-src-dir",  # No src directory
                "--import-alias", "@/*"  # Path alias
            ])

            self.logger.info(f"Running: {' '.join(cmd)}")

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info("Next.js project created successfully")
            self.logger.debug(f"Output: {result.stdout}")

            # Verify created files
            project_path = Path("frontend")
            package_json = project_path / "package.json"
            tsconfig = project_path / "tsconfig.json" if use_typescript else None

            artifacts = [str(project_path)]
            if package_json.exists():
                artifacts.append(str(package_json))
            if tsconfig and tsconfig.exists():
                artifacts.append(str(tsconfig))

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "project_path": str(project_path),
                    "package_json_path": str(package_json),
                    "tsconfig_path": str(tsconfig) if tsconfig else None
                },
                artifacts=artifacts,
                logs=[result.stdout]
            )

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create Next.js project: {e.stderr}")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=f"Command failed: {e.stderr}",
                logs=[e.stdout, e.stderr]
            )
        except Exception as e:
            self.logger.exception("Unexpected error")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Project created in frontend/ directory",
            "package.json contains Next.js 16+",
            "TypeScript configuration present",
            "App Router structure (app/ directory)",
            "npm install completes successfully"
        ]
