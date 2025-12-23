"""
Skill FE-002: Create React Component

Creates a new React component with TypeScript types and proper structure.
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
class CreateReactComponentSkill(Skill):
    """Create a new React component."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="FE-002",
            name="Create React Component",
            description="Create a new React component with TypeScript types and proper structure",
            category="frontend",
            version="1.0.0",
            dependencies=["FE-001"],  # Requires Next.js project
            inputs_schema={
                "type": "object",
                "properties": {
                    "component_name": {"type": "string"},
                    "component_type": {
                        "type": "string",
                        "enum": ["page", "component", "layout"],
                        "default": "component"
                    },
                    "props": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "optional": {"type": "boolean", "default": False}
                            }
                        },
                        "default": []
                    },
                    "use_client": {"type": "boolean", "default": False}
                },
                "required": ["component_name"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "component_path": {"type": "string"},
                    "component_type": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        # Check required parameters
        if "component_name" not in params:
            return False, "Missing required parameter: component_name"

        component_name = params["component_name"]
        if not isinstance(component_name, str) or not component_name:
            return False, "component_name must be a non-empty string"

        # Validate component type
        component_type = params.get("component_type", "component")
        if component_type not in ["page", "component", "layout"]:
            return False, f"Invalid component_type: {component_type}"

        # Check if frontend directory exists
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            return False, "Frontend directory does not exist. Run FE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        component_name = params["component_name"]
        component_type = params.get("component_type", "component")
        props = params.get("props", [])
        use_client = params.get("use_client", False)

        try:
            # Determine component path
            frontend_path = Path("frontend")
            if component_type == "page":
                component_dir = frontend_path / "app" / component_name.lower()
                component_file = component_dir / "page.tsx"
            elif component_type == "layout":
                component_dir = frontend_path / "app" / component_name.lower()
                component_file = component_dir / "layout.tsx"
            else:  # component
                component_dir = frontend_path / "components"
                component_file = component_dir / f"{component_name}.tsx"

            # Create directory if needed
            component_dir.mkdir(parents=True, exist_ok=True)

            # Generate props interface
            props_interface = ""
            if props:
                props_lines = []
                for prop in props:
                    prop_name = prop["name"]
                    prop_type = prop["type"]
                    optional = prop.get("optional", False)
                    optional_marker = "?" if optional else ""
                    props_lines.append(f"  {prop_name}{optional_marker}: {prop_type}")

                props_interface = f"""interface {component_name}Props {{
{chr(10).join(props_lines)}
}}

"""

            # Generate component code
            client_directive = '"use client"\n\n' if use_client else ""

            if props:
                component_params = f"{{ {', '.join(p['name'] for p in props)} }}: {component_name}Props"
            else:
                component_params = ""

            component_code = f"""{client_directive}{props_interface}export default function {component_name}({component_params}) {{
  return (
    <div>
      <h1>{component_name}</h1>
      {/* Component content */}
    </div>
  )
}}
"""

            # Write component file
            component_file.write_text(component_code, encoding="utf-8")

            self.logger.info(f"Created {component_type} component: {component_file}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "component_path": str(component_file),
                    "component_type": component_type
                },
                artifacts=[str(component_file)],
                logs=[f"Created {component_type}: {component_file}"]
            )

        except Exception as e:
            self.logger.exception("Failed to create component")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Component file created in correct directory",
            "TypeScript interface defined for props (if any)",
            "Component exports default function",
            "Component includes proper type annotations",
            "'use client' directive added if required"
        ]
