"""
Skill BE-001: Initialize FastAPI Project

Creates a new FastAPI application with proper structure and dependencies.
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
class InitFastAPIProjectSkill(Skill):
    """Initialize a new FastAPI project."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="BE-001",
            name="Initialize FastAPI Project",
            description="Create a new FastAPI application with proper structure and dependencies",
            category="backend",
            version="1.0.0",
            dependencies=[],
            inputs_schema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "default": "backend"
                    },
                    "python_version": {
                        "type": "string",
                        "default": "3.11"
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string"},
                    "requirements_path": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        project_name = inputs.params.get("project_name", "backend")
        project_path = Path(project_name)

        if project_path.exists():
            return False, f"Directory already exists: {project_path}"

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        project_name = params.get("project_name", "backend")
        python_version = params.get("python_version", "3.11")

        try:
            # Create project structure
            project_path = Path(project_name)
            project_path.mkdir(parents=True, exist_ok=True)

            # Create directory structure
            (project_path / "app").mkdir(exist_ok=True)
            (project_path / "app" / "api").mkdir(exist_ok=True)
            (project_path / "app" / "api" / "endpoints").mkdir(exist_ok=True)
            (project_path / "app" / "core").mkdir(exist_ok=True)
            (project_path / "app" / "models").mkdir(exist_ok=True)
            (project_path / "app" / "schemas").mkdir(exist_ok=True)
            (project_path / "app" / "db").mkdir(exist_ok=True)
            (project_path / "tests").mkdir(exist_ok=True)

            self.logger.info(f"Created project structure: {project_path}")

            # Create __init__.py files
            (project_path / "app" / "__init__.py").touch()
            (project_path / "app" / "api" / "__init__.py").touch()
            (project_path / "app" / "api" / "endpoints" / "__init__.py").touch()
            (project_path / "app" / "core" / "__init__.py").touch()
            (project_path / "app" / "models" / "__init__.py").touch()
            (project_path / "app" / "schemas" / "__init__.py").touch()
            (project_path / "app" / "db" / "__init__.py").touch()
            (project_path / "tests" / "__init__.py").touch()

            # Create main.py
            main_py_path = project_path / "app" / "main.py"
            main_py_code = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import auth, tasks

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(tasks.router, prefix=settings.API_PREFIX, tags=["tasks"])


@app.get("/")
async def root():
    return {"message": "Todo API", "version": settings.VERSION}


@app.get("/health")
async def health():
    return {"status": "healthy"}
"""
            main_py_path.write_text(main_py_code, encoding="utf-8")

            # Create config.py
            config_py_path = project_path / "app" / "core" / "config.py"
            config_py_code = """from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Todo API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
"""
            config_py_path.write_text(config_py_code, encoding="utf-8")

            # Create requirements.txt
            requirements_path = project_path / "requirements.txt"
            requirements = """fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic-settings==2.1.0
pytest==7.4.4
httpx==0.26.0
"""
            requirements_path.write_text(requirements, encoding="utf-8")

            # Create .env.example
            env_example_path = project_path / ".env.example"
            env_example = """# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]
"""
            env_example_path.write_text(env_example, encoding="utf-8")

            # Create pytest.ini
            pytest_ini_path = project_path / "pytest.ini"
            pytest_ini = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
"""
            pytest_ini_path.write_text(pytest_ini, encoding="utf-8")

            # Create .gitignore
            gitignore_path = project_path / ".gitignore"
            gitignore = """__pycache__/
*.py[cod]
*$py.class
.env
.venv
venv/
ENV/
env/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
"""
            gitignore_path.write_text(gitignore, encoding="utf-8")

            artifacts = [
                str(project_path),
                str(main_py_path),
                str(config_py_path),
                str(requirements_path),
                str(env_example_path),
                str(pytest_ini_path),
                str(gitignore_path)
            ]

            self.logger.info(f"FastAPI project initialized: {project_path}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "project_path": str(project_path),
                    "requirements_path": str(requirements_path)
                },
                artifacts=artifacts,
                logs=[f"Created FastAPI project with {len(artifacts)} files"]
            )

        except Exception as e:
            self.logger.exception("Failed to initialize FastAPI project")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Project directory structure created",
            "main.py with FastAPI app and routers",
            "config.py with settings management",
            "requirements.txt with all dependencies",
            ".env.example with configuration template",
            "pytest.ini for test configuration",
            ".gitignore for Python projects",
            "All __init__.py files created"
        ]
