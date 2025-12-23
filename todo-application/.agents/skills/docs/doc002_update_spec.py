"""
Skill DOC-002: Update Specification Document

Updates specification documents based on implementation changes.
"""

from pathlib import Path
from typing import List
from datetime import datetime
from ...lib.skill_base import (
    Skill,
    SkillMetadata,
    SkillInput,
    SkillOutput,
    SkillStatus,
    register_skill
)


@register_skill
class UpdateSpecificationSkill(Skill):
    """Update specification documents."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DOC-002",
            name="Update Specification Document",
            description="Update specification documents based on implementation changes",
            category="docs",
            version="1.0.0",
            dependencies=[],
            inputs_schema={
                "type": "object",
                "properties": {
                    "spec_path": {"type": "string"},
                    "section": {"type": "string"},
                    "content": {"type": "string"},
                    "append": {"type": "boolean", "default": False}
                },
                "required": ["spec_path", "section", "content"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "spec_path": {"type": "string"},
                    "updated": {"type": "boolean"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        required = ["spec_path", "section", "content"]
        for field in required:
            if field not in params:
                return False, f"Missing required parameter: {field}"

        spec_path = Path(params["spec_path"])
        if not spec_path.exists():
            return False, f"Specification file does not exist: {spec_path}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        spec_path = Path(params["spec_path"])
        section = params["section"]
        content = params["content"]
        append = params.get("append", False)

        try:
            # Read existing spec
            spec_content = spec_path.read_text(encoding="utf-8")

            # Update spec
            if append:
                # Append to section
                section_marker = f"## {section}"
                if section_marker in spec_content:
                    # Find the section and append
                    lines = spec_content.split("\n")
                    insert_index = -1

                    for i, line in enumerate(lines):
                        if line.strip() == section_marker:
                            # Find next section or end of file
                            for j in range(i + 1, len(lines)):
                                if lines[j].startswith("## "):
                                    insert_index = j
                                    break
                            if insert_index == -1:
                                insert_index = len(lines)
                            break

                    if insert_index > 0:
                        lines.insert(insert_index, f"\n{content}\n")
                        spec_content = "\n".join(lines)
                else:
                    # Section doesn't exist, add it at the end
                    spec_content += f"\n\n## {section}\n\n{content}\n"

            else:
                # Replace section content
                section_marker = f"## {section}"
                if section_marker in spec_content:
                    lines = spec_content.split("\n")
                    section_start = -1
                    section_end = -1

                    # Find section boundaries
                    for i, line in enumerate(lines):
                        if line.strip() == section_marker:
                            section_start = i
                            # Find next section
                            for j in range(i + 1, len(lines)):
                                if lines[j].startswith("## "):
                                    section_end = j
                                    break
                            if section_end == -1:
                                section_end = len(lines)
                            break

                    if section_start >= 0:
                        # Replace section content
                        new_lines = lines[:section_start + 1] + [f"\n{content}\n"] + lines[section_end:]
                        spec_content = "\n".join(new_lines)
                else:
                    # Section doesn't exist, add it
                    spec_content += f"\n\n## {section}\n\n{content}\n"

            # Add update timestamp
            update_note = f"\n\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            if "*Last updated:" in spec_content:
                # Replace existing timestamp
                lines = spec_content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("*Last updated:"):
                        lines[i] = update_note.strip()
                        break
                spec_content = "\n".join(lines)
            else:
                spec_content += update_note

            # Write updated spec
            spec_path.write_text(spec_content, encoding="utf-8")

            self.logger.info(f"Updated specification section '{section}' in {spec_path}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "spec_path": str(spec_path),
                    "updated": True
                },
                artifacts=[str(spec_path)],
                logs=[f"Updated section '{section}'"]
            )

        except Exception as e:
            self.logger.exception("Failed to update specification")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Specification file updated",
            "Section content replaced or appended",
            "Markdown formatting preserved",
            "Timestamp added/updated",
            "File encoding maintained (UTF-8)",
            "No corruption of existing content"
        ]
