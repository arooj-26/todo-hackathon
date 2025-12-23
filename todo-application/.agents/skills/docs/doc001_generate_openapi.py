"""
Skill DOC-001: Generate OpenAPI Schema

Generates OpenAPI/Swagger documentation from FastAPI application.
"""

from pathlib import Path
from typing import List
import json
from ...lib.skill_base import (
    Skill,
    SkillMetadata,
    SkillInput,
    SkillOutput,
    SkillStatus,
    register_skill
)


@register_skill
class GenerateOpenAPISchemaSkill(Skill):
    """Generate OpenAPI schema documentation."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DOC-001",
            name="Generate OpenAPI Schema",
            description="Generate OpenAPI/Swagger documentation from FastAPI application",
            category="docs",
            version="1.0.0",
            dependencies=["BE-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "yaml"],
                        "default": "yaml"
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "schema_path": {"type": "string"},
                    "format": {"type": "string"}
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
        output_format = params.get("output_format", "yaml")

        try:
            backend_path = Path("backend")
            docs_dir = backend_path / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)

            # Import the FastAPI app
            import sys
            sys.path.insert(0, str(backend_path))

            try:
                from app.main import app

                # Get OpenAPI schema
                openapi_schema = app.openapi()

                # Write schema to file
                if output_format == "json":
                    schema_path = docs_dir / "openapi.json"
                    with open(schema_path, "w", encoding="utf-8") as f:
                        json.dump(openapi_schema, f, indent=2)
                else:  # yaml
                    schema_path = docs_dir / "openapi.yaml"
                    try:
                        import yaml
                        with open(schema_path, "w", encoding="utf-8") as f:
                            yaml.dump(openapi_schema, f, default_flow_style=False, sort_keys=False)
                    except ImportError:
                        # Fall back to JSON if PyYAML not available
                        self.logger.warning("PyYAML not installed, generating JSON instead")
                        schema_path = docs_dir / "openapi.json"
                        with open(schema_path, "w", encoding="utf-8") as f:
                            json.dump(openapi_schema, f, indent=2)
                        output_format = "json"

                self.logger.info(f"Generated OpenAPI schema: {schema_path}")

                # Create README for docs
                readme_path = docs_dir / "README.md"
                readme_content = f"""# API Documentation

This directory contains the OpenAPI schema for the Todo API.

## Files

- `{schema_path.name}`: OpenAPI 3.0 schema definition

## Viewing the Documentation

### Using Swagger UI

Run the FastAPI application and navigate to:
- http://localhost:8000/docs

### Using ReDoc

Run the FastAPI application and navigate to:
- http://localhost:8000/redoc

### Using External Tools

You can also view the schema using:
- [Swagger Editor](https://editor.swagger.io/)
- [Redocly](https://redocly.github.io/redoc/)
- [Postman](https://www.postman.com/) (import the schema)

## Generating Updated Schema

To regenerate the schema after API changes:

```bash
cd backend
python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > docs/openapi.json
```
"""

                readme_path.write_text(readme_content, encoding="utf-8")

                artifacts = [str(schema_path), str(readme_path)]

                return SkillOutput(
                    status=SkillStatus.SUCCESS,
                    result={
                        "schema_path": str(schema_path),
                        "format": output_format
                    },
                    artifacts=artifacts,
                    logs=[f"Generated OpenAPI schema in {output_format} format"]
                )

            except Exception as import_error:
                self.logger.error(f"Failed to import FastAPI app: {import_error}")
                return SkillOutput(
                    status=SkillStatus.FAILED,
                    error=f"Could not import FastAPI app: {str(import_error)}"
                )

        except Exception as e:
            self.logger.exception("Failed to generate OpenAPI schema")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "OpenAPI schema file generated",
            "Schema includes all endpoints",
            "Request/response models documented",
            "Authentication schemes defined",
            "README created with usage instructions",
            "Schema valid OpenAPI 3.0 format",
            "Can be viewed in Swagger UI/ReDoc"
        ]
