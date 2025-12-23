"""
Skill TEST-001: Write Backend Unit Test

Creates pytest unit tests for backend functions and classes.
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
class WriteBackendUnitTestSkill(Skill):
    """Write unit tests for backend code."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="TEST-001",
            name="Write Backend Unit Test",
            description="Create pytest unit tests for backend functions and classes",
            category="testing",
            version="1.0.0",
            dependencies=["BE-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "module_path": {"type": "string"},
                    "function_name": {"type": "string"},
                    "test_scenarios": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["success case", "error case"]
                    }
                },
                "required": ["module_path", "function_name"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "test_file_path": {"type": "string"},
                    "scenarios_count": {"type": "integer"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        required = ["module_path", "function_name"]
        for field in required:
            if field not in params:
                return False, f"Missing required parameter: {field}"

        module_path = Path(params["module_path"])
        if not module_path.exists():
            return False, f"Module file does not exist: {module_path}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        module_path = Path(params["module_path"])
        function_name = params["function_name"]
        test_scenarios = params.get("test_scenarios", ["success case", "error case"])

        try:
            # Determine test file path
            backend_path = Path("backend")

            # Convert module path to import path
            relative_path = module_path.relative_to(backend_path / "app")
            import_parts = [p for p in relative_path.parts if p != "__pycache__"]
            import_parts[-1] = import_parts[-1].replace(".py", "")
            import_path = "app." + ".".join(import_parts)

            # Create test file in tests directory
            test_dir = backend_path / "tests"
            test_module_dir = test_dir / relative_path.parent
            test_module_dir.mkdir(parents=True, exist_ok=True)

            test_file_path = test_module_dir / f"test_{module_path.stem}.py"

            # Generate test code
            test_imports = f"""import pytest
from {import_path} import {function_name}
"""

            # Generate test cases
            test_cases = []

            for scenario in test_scenarios:
                scenario_lower = scenario.lower()

                if "success" in scenario_lower or "valid" in scenario_lower:
                    test_cases.append(f"""
def test_{function_name}_success():
    \"\"\"Test {function_name} with valid inputs.\"\"\"
    # Arrange
    # TODO: Set up test data

    # Act
    result = {function_name}()

    # Assert
    # TODO: Add assertions
    assert result is not None
""")

                elif "error" in scenario_lower or "invalid" in scenario_lower:
                    test_cases.append(f"""
def test_{function_name}_error():
    \"\"\"Test {function_name} with invalid inputs.\"\"\"
    # Arrange
    # TODO: Set up invalid test data

    # Act & Assert
    with pytest.raises(Exception):
        {function_name}()
""")

                elif "edge" in scenario_lower:
                    test_cases.append(f"""
def test_{function_name}_edge_case():
    \"\"\"Test {function_name} with edge case inputs.\"\"\"
    # Arrange
    # TODO: Set up edge case data

    # Act
    result = {function_name}()

    # Assert
    # TODO: Add assertions
    assert result is not None
""")

            test_code = test_imports + "\n".join(test_cases)

            # Write test file
            test_file_path.write_text(test_code, encoding="utf-8")

            self.logger.info(f"Created unit test: {test_file_path}")

            # Ensure __init__.py files exist in test directories
            current_dir = test_module_dir
            while current_dir != test_dir.parent:
                init_file = current_dir / "__init__.py"
                init_file.touch(exist_ok=True)
                current_dir = current_dir.parent

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "test_file_path": str(test_file_path),
                    "scenarios_count": len(test_cases)
                },
                artifacts=[str(test_file_path)],
                logs=[f"Created {len(test_cases)} test scenarios"]
            )

        except Exception as e:
            self.logger.exception("Failed to create unit test")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Test file created in tests/ directory",
            "pytest fixtures and imports included",
            "Test functions follow naming convention (test_*)",
            "Arrange-Act-Assert pattern used",
            "Success and error cases covered",
            "Test docstrings present",
            "__init__.py files in test directories"
        ]
