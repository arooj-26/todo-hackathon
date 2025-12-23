"""
Skill TEST-003: Write Frontend Component Test

Creates Jest and React Testing Library tests for React components.
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
class WriteFrontendComponentTestSkill(Skill):
    """Write tests for React components."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="TEST-003",
            name="Write Frontend Component Test",
            description="Create Jest and React Testing Library tests for React components",
            category="testing",
            version="1.0.0",
            dependencies=["FE-002"],  # Requires component
            inputs_schema={
                "type": "object",
                "properties": {
                    "component_path": {"type": "string"},
                    "component_name": {"type": "string"},
                    "test_scenarios": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["renders correctly", "handles user interaction"]
                    }
                },
                "required": ["component_path", "component_name"]
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

        if "component_path" not in params:
            return False, "Missing required parameter: component_path"

        if "component_name" not in params:
            return False, "Missing required parameter: component_name"

        component_path = Path(params["component_path"])
        if not component_path.exists():
            return False, f"Component file does not exist: {component_path}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        component_path = Path(params["component_path"])
        component_name = params["component_name"]
        test_scenarios = params.get("test_scenarios", ["renders correctly", "handles user interaction"])

        try:
            # Determine test file path
            if component_path.parent.name == "app":
                # Page component
                test_file_path = component_path.parent / "page.test.tsx"
            else:
                # Regular component
                test_file_path = component_path.with_suffix(".test.tsx")

            # Generate test code
            test_imports = f"""import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react'
import '@testing-library/jest-dom'
import {component_name} from './{component_path.stem}'
"""

            # Generate test scenarios
            test_cases = []

            # Basic render test
            test_cases.append(f"""  it('renders without crashing', () => {{
    render(<{component_name} />)
    expect(screen.getByText('{component_name}')).toBeInTheDocument()
  }})
""")

            # Scenario-based tests
            for scenario in test_scenarios:
                if "renders correctly" in scenario.lower():
                    test_cases.append(f"""  it('renders all expected elements', () => {{
    render(<{component_name} />)
    // Add assertions for expected elements
    expect(screen.getByRole('heading')).toBeInTheDocument()
  }})
""")
                elif "user interaction" in scenario.lower() or "click" in scenario.lower():
                    test_cases.append(f"""  it('handles user interactions', async () => {{
    render(<{component_name} />)
    // Simulate user interaction
    // const button = screen.getByRole('button')
    // fireEvent.click(button)
    // await waitFor(() => {{
    //   expect(screen.getByText('Expected Result')).toBeInTheDocument()
    // }})
  }})
""")
                elif "props" in scenario.lower():
                    test_cases.append(f"""  it('displays props correctly', () => {{
    const testProps = {{
      // Add test props
    }}
    render(<{component_name} {{...testProps}} />)
    // Add assertions
  }})
""")
                elif "error" in scenario.lower():
                    test_cases.append(f"""  it('handles errors gracefully', () => {{
    // Test error scenarios
    render(<{component_name} />)
    // Add error assertions
  }})
""")

            test_code = f"""{test_imports}
describe('{component_name}', () => {{
{chr(10).join(test_cases)}
}})
"""

            # Write test file
            test_file_path.write_text(test_code, encoding="utf-8")

            self.logger.info(f"Created test file: {test_file_path}")

            # Ensure Jest config exists
            frontend_path = Path("frontend")
            jest_config_path = frontend_path / "jest.config.js"

            if not jest_config_path.exists():
                jest_config = """const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
"""
                jest_config_path.write_text(jest_config, encoding="utf-8")
                self.logger.info(f"Created Jest config: {jest_config_path}")

            # Ensure Jest setup file exists
            jest_setup_path = frontend_path / "jest.setup.js"
            if not jest_setup_path.exists():
                jest_setup = """// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'
"""
                jest_setup_path.write_text(jest_setup, encoding="utf-8")
                self.logger.info(f"Created Jest setup: {jest_setup_path}")

            artifacts = [str(test_file_path), str(jest_config_path), str(jest_setup_path)]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "test_file_path": str(test_file_path),
                    "scenarios_count": len(test_cases)
                },
                artifacts=artifacts,
                logs=[f"Created test with {len(test_cases)} scenarios"]
            )

        except Exception as e:
            self.logger.exception("Failed to create component test")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Test file created with .test.tsx extension",
            "Jest and React Testing Library imports included",
            "Render test validates component mounts",
            "User interaction tests use fireEvent and waitFor",
            "Props tests validate data binding",
            "Jest config configured for Next.js",
            "Test setup file includes jest-dom matchers"
        ]
