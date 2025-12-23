"""
Skill DB-001: Define Database Schema

Creates SQLModel database models with proper types and relationships.
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
class DefineDatabaseSchemaSkill(Skill):
    """Define database schema with SQLModel."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DB-001",
            name="Define Database Schema",
            description="Create SQLModel database models with proper types and relationships",
            category="database",
            version="1.0.0",
            dependencies=["BE-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "model_name": {"type": "string"},
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "optional": {"type": "boolean", "default": False},
                                "default": {"type": "string"},
                                "unique": {"type": "boolean", "default": False},
                                "index": {"type": "boolean", "default": False},
                                "foreign_key": {"type": "string"}
                            },
                            "required": ["name", "type"]
                        }
                    },
                    "table_name": {"type": "string"},
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "model": {"type": "string"},
                                "back_populates": {"type": "string"}
                            }
                        },
                        "default": []
                    }
                },
                "required": ["model_name", "fields"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "model_path": {"type": "string"},
                    "model_name": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        if "model_name" not in params:
            return False, "Missing required parameter: model_name"

        if "fields" not in params or not params["fields"]:
            return False, "Missing required parameter: fields"

        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        model_name = params["model_name"]
        fields = params["fields"]
        table_name = params.get("table_name", model_name.lower() + "s")
        relationships = params.get("relationships", [])

        try:
            backend_path = Path("backend")
            models_path = backend_path / "app" / "models"
            model_file_path = models_path / f"{model_name.lower()}.py"

            # Generate imports
            imports = """from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
"""

            # Generate field definitions
            field_defs = []
            for field in fields:
                field_name = field["name"]
                field_type = field["type"]
                optional = field.get("optional", False)
                default = field.get("default")
                unique = field.get("unique", False)
                index = field.get("index", False)
                foreign_key = field.get("foreign_key")

                # Build field type
                if optional:
                    type_str = f"Optional[{field_type}]"
                else:
                    type_str = field_type

                # Build Field parameters
                field_params = []

                if field_name == "id":
                    field_params.append("default=None")
                    field_params.append("primary_key=True")
                elif default:
                    field_params.append(f"default={default}")
                elif field_type == "datetime":
                    field_params.append("default_factory=datetime.utcnow")

                if unique:
                    field_params.append("unique=True")
                if index:
                    field_params.append("index=True")
                if foreign_key:
                    field_params.append(f'foreign_key="{foreign_key}"')

                if not optional and default is None and field_name != "id":
                    field_params.append("nullable=False")

                if field_params:
                    field_def = f'    {field_name}: {type_str} = Field({", ".join(field_params)})'
                else:
                    field_def = f'    {field_name}: {type_str}'

                field_defs.append(field_def)

            # Generate relationship definitions
            rel_defs = []
            for rel in relationships:
                rel_name = rel["name"]
                rel_model = rel["model"]
                back_populates = rel.get("back_populates", "")

                if back_populates:
                    rel_def = f'    {rel_name}: List["{rel_model}"] = Relationship(back_populates="{back_populates}")'
                else:
                    rel_def = f'    {rel_name}: List["{rel_model}"] = Relationship()'

                rel_defs.append(rel_def)

            # Generate model class
            model_code = f"""{imports}

class {model_name}(SQLModel, table=True):
    \"\"\"
    {model_name} model.

    Represents {table_name} table in the database.
    \"\"\"
    __tablename__ = "{table_name}"

{chr(10).join(field_defs)}
{chr(10).join(rel_defs) if rel_defs else ""}
"""

            # Write model file
            model_file_path.write_text(model_code, encoding="utf-8")

            self.logger.info(f"Created database model: {model_file_path}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "model_path": str(model_file_path),
                    "model_name": model_name
                },
                artifacts=[str(model_file_path)],
                logs=[f"Created {model_name} model with {len(fields)} fields"]
            )

        except Exception as e:
            self.logger.exception("Failed to define database schema")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "SQLModel class created with table=True",
            "All fields defined with proper types",
            "Primary key (id) defined",
            "Foreign keys configured correctly",
            "Indexes created where needed",
            "Unique constraints applied",
            "Relationships defined with back_populates",
            "Table name specified with __tablename__"
        ]
