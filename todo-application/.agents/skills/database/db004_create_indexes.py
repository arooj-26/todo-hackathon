"""
Skill DB-004: Create Database Indexes

Creates database indexes for performance optimization.
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
class CreateDatabaseIndexesSkill(Skill):
    """Create database indexes."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DB-004",
            name="Create Database Indexes",
            description="Create database indexes for performance optimization",
            category="database",
            version="1.0.0",
            dependencies=["DB-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string"},
                    "indexes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "columns": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "unique": {"type": "boolean", "default": False}
                            },
                            "required": ["name", "columns"]
                        }
                    }
                },
                "required": ["model_name", "indexes"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "model_path": {"type": "string"},
                    "indexes_created": {"type": "integer"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        if "model_name" not in params:
            return False, "Missing required parameter: model_name"

        if "indexes" not in params:
            return False, "Missing required parameter: indexes"

        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        model_name = params["model_name"]
        model_path = backend_path / "app" / "models" / f"{model_name.lower()}.py"
        if not model_path.exists():
            return False, f"Model file does not exist: {model_path}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        model_name = params["model_name"]
        indexes = params["indexes"]

        try:
            backend_path = Path("backend")
            model_path = backend_path / "app" / "models" / f"{model_name.lower()}.py"

            # Read existing model
            model_content = model_path.read_text(encoding="utf-8")

            # Check if Index is imported
            if "from sqlalchemy import Index" not in model_content:
                # Add Index import
                if "from sqlmodel import" in model_content:
                    model_content = model_content.replace(
                        "from sqlmodel import",
                        "from sqlalchemy import Index\nfrom sqlmodel import"
                    )
                else:
                    model_content = "from sqlalchemy import Index\n" + model_content

            # Generate index definitions
            index_defs = []

            for idx in indexes:
                idx_name = idx["name"]
                columns = idx["columns"]
                unique = idx.get("unique", False)

                # Build index definition
                columns_str = ", ".join([f'"{col}"' for col in columns])
                unique_str = ", unique=True" if unique else ""

                index_def = f'    Index("{idx_name}", {columns_str}{unique_str}),'

                index_defs.append(index_def)

            # Add __table_args__ to model class
            table_args_block = f"""
    __table_args__ = (
{chr(10).join(index_defs)}
    )
"""

            # Check if __table_args__ already exists
            if "__table_args__" in model_content:
                self.logger.warning("__table_args__ already exists, appending indexes")
                # Find and update existing __table_args__
                lines = model_content.split("\n")
                insert_index = -1

                for i, line in enumerate(lines):
                    if "__table_args__ = (" in line:
                        # Find closing parenthesis
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip() == ")":
                                insert_index = j
                                break
                        break

                if insert_index > 0:
                    # Insert indexes before closing parenthesis
                    for idx_def in index_defs:
                        lines.insert(insert_index, idx_def)
                        insert_index += 1

                    model_content = "\n".join(lines)
            else:
                # Add __table_args__ after __tablename__
                if "__tablename__" in model_content:
                    model_content = model_content.replace(
                        '__tablename__',
                        f'__tablename__\n{table_args_block}\n    # Fields'
                    )

            # Write updated model
            model_path.write_text(model_content, encoding="utf-8")

            self.logger.info(f"Added {len(indexes)} indexes to {model_name}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "model_path": str(model_path),
                    "indexes_created": len(indexes)
                },
                artifacts=[str(model_path)],
                logs=[f"Created {len(indexes)} indexes"]
            )

        except Exception as e:
            self.logger.exception("Failed to create database indexes")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Index import added to model",
            "__table_args__ tuple created or updated",
            "Single-column indexes defined",
            "Multi-column composite indexes defined",
            "Unique indexes marked correctly",
            "Index names follow convention (idx_table_column)",
            "Indexes improve query performance for filtered columns",
            "Foreign key columns indexed"
        ]
