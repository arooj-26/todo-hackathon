"""
Skill DEVOPS-001: Create Docker Compose Configuration

Creates Docker Compose configuration for local development.
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
class CreateDockerComposeSkill(Skill):
    """Create Docker Compose configuration."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DEVOPS-001",
            name="Create Docker Compose Configuration",
            description="Create Docker Compose configuration for local development",
            category="devops",
            version="1.0.0",
            dependencies=[],
            inputs_schema={
                "type": "object",
                "properties": {
                    "include_postgres": {"type": "boolean", "default": True},
                    "include_redis": {"type": "boolean", "default": False}
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "compose_file_path": {"type": "string"},
                    "created": {"type": "boolean"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        include_postgres = params.get("include_postgres", True)
        include_redis = params.get("include_redis", False)

        try:
            compose_file_path = Path("docker-compose.yml")

            # Generate Docker Compose configuration
            compose_content = """version: '3.8'

services:"""

            # Add backend service
            compose_content += """
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_ORIGINS=["http://localhost:3000"]
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:"""

            if include_postgres:
                compose_content += """
      - postgres"""

            # Add frontend service
            compose_content += """

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_APP_URL=http://localhost:3000
    env_file:
      - ./frontend/.env
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev
    depends_on:
      - backend"""

            # Add PostgreSQL service if requested
            if include_postgres:
                compose_content += """

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=todouser
      - POSTGRES_PASSWORD=todopassword
      - POSTGRES_DB=tododb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todouser"]
      interval: 10s
      timeout: 5s
      retries: 5"""

            # Add Redis service if requested
            if include_redis:
                compose_content += """

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5"""

            # Add volumes section
            compose_content += """

volumes:"""

            if include_postgres:
                compose_content += """
  postgres_data:"""

            if include_redis:
                compose_content += """
  redis_data:"""

            compose_content += "\n"

            # Write docker-compose.yml
            compose_file_path.write_text(compose_content, encoding="utf-8")
            self.logger.info(f"Created docker-compose.yml: {compose_file_path}")

            # Create backend Dockerfile
            backend_path = Path("backend")
            if backend_path.exists():
                backend_dockerfile = backend_path / "Dockerfile"
                backend_dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
                backend_dockerfile.write_text(backend_dockerfile_content, encoding="utf-8")
                self.logger.info(f"Created backend Dockerfile: {backend_dockerfile}")

            # Create frontend Dockerfile
            frontend_path = Path("frontend")
            if frontend_path.exists():
                frontend_dockerfile = frontend_path / "Dockerfile"
                frontend_dockerfile_content = """FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "run", "dev"]
"""
                frontend_dockerfile.write_text(frontend_dockerfile_content, encoding="utf-8")
                self.logger.info(f"Created frontend Dockerfile: {frontend_dockerfile}")

            # Create .dockerignore files
            backend_dockerignore = backend_path / ".dockerignore" if backend_path.exists() else None
            if backend_dockerignore:
                backend_dockerignore_content = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
venv
.venv
.env
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
.git
.gitignore
"""
                backend_dockerignore.write_text(backend_dockerignore_content, encoding="utf-8")

            frontend_dockerignore = frontend_path / ".dockerignore" if frontend_path.exists() else None
            if frontend_dockerignore:
                frontend_dockerignore_content = """node_modules
.next
.git
.gitignore
.env
.env.local
npm-debug.log
yarn-debug.log
yarn-error.log
"""
                frontend_dockerignore.write_text(frontend_dockerignore_content, encoding="utf-8")

            artifacts = [str(compose_file_path)]
            if backend_dockerfile and backend_dockerfile.exists():
                artifacts.append(str(backend_dockerfile))
            if frontend_dockerfile and frontend_dockerfile.exists():
                artifacts.append(str(frontend_dockerfile))

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "compose_file_path": str(compose_file_path),
                    "created": True
                },
                artifacts=artifacts,
                logs=["Created Docker Compose configuration with all services"]
            )

        except Exception as e:
            self.logger.exception("Failed to create Docker Compose configuration")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "docker-compose.yml created",
            "Backend service defined with correct ports",
            "Frontend service defined with correct ports",
            "Database service configured (if included)",
            "Volume mounts for development",
            "Environment variables configured",
            "Health checks for database services",
            "Dockerfiles created for backend and frontend",
            ".dockerignore files created"
        ]
