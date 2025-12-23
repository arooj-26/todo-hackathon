"""
Skill DEVOPS-002: Configure Environment Variables

Creates and configures environment variable files for different environments.
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
class ConfigureEnvironmentVariablesSkill(Skill):
    """Configure environment variables."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DEVOPS-002",
            name="Configure Environment Variables",
            description="Create and configure environment variable files for different environments",
            category="devops",
            version="1.0.0",
            dependencies=[],
            inputs_schema={
                "type": "object",
                "properties": {
                    "environment": {
                        "type": "string",
                        "enum": ["development", "staging", "production"],
                        "default": "development"
                    },
                    "variables": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "env_files_created": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        environment = params.get("environment", "development")
        custom_vars = params.get("variables", {})

        try:
            artifacts = []

            # Backend .env.example
            backend_path = Path("backend")
            if backend_path.exists():
                backend_env_example = backend_path / ".env.example"
                backend_env_content = """# Database Configuration
# For local development with docker-compose
DATABASE_URL=postgresql://todouser:todopassword@localhost:5432/tododb
# For Neon PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@host.neon.tech:5432/dbname?sslmode=require

# Security
SECRET_KEY=your-secret-key-change-in-production-use-secrets-manager
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# CORS - Allowed Origins (comma-separated for multiple origins)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# Application
PROJECT_NAME=Todo API
VERSION=1.0.0
API_PREFIX=/api

# Environment
ENVIRONMENT=development
"""

                # Add custom variables
                if custom_vars:
                    backend_env_content += "\n# Custom Variables\n"
                    for key, value in custom_vars.items():
                        backend_env_content += f"{key}={value}\n"

                backend_env_example.write_text(backend_env_content, encoding="utf-8")
                artifacts.append(str(backend_env_example))
                self.logger.info(f"Created backend .env.example: {backend_env_example}")

                # Create actual .env if it doesn't exist
                backend_env = backend_path / ".env"
                if not backend_env.exists():
                    backend_env.write_text(backend_env_content, encoding="utf-8")
                    artifacts.append(str(backend_env))
                    self.logger.info(f"Created backend .env: {backend_env}")

            # Frontend .env.example
            frontend_path = Path("frontend")
            if frontend_path.exists():
                frontend_env_example = frontend_path / ".env.example"
                frontend_env_content = """# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Better Auth
BETTER_AUTH_SECRET=your-auth-secret-change-in-production
BETTER_AUTH_URL=http://localhost:3000

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
"""

                # Add custom variables
                if custom_vars:
                    frontend_env_content += "\n# Custom Variables\n"
                    for key, value in custom_vars.items():
                        if key.startswith("NEXT_PUBLIC_"):
                            frontend_env_content += f"{key}={value}\n"

                frontend_env_example.write_text(frontend_env_content, encoding="utf-8")
                artifacts.append(str(frontend_env_example))
                self.logger.info(f"Created frontend .env.example: {frontend_env_example}")

                # Create actual .env.local if it doesn't exist
                frontend_env = frontend_path / ".env.local"
                if not frontend_env.exists():
                    frontend_env.write_text(frontend_env_content, encoding="utf-8")
                    artifacts.append(str(frontend_env))
                    self.logger.info(f"Created frontend .env.local: {frontend_env}")

            # Create root .env for docker-compose
            root_env_example = Path(".env.example")
            root_env_content = """# Root environment file for docker-compose

# Database (for docker-compose PostgreSQL service)
POSTGRES_USER=todouser
POSTGRES_PASSWORD=todopassword
POSTGRES_DB=tododb

# Backend
DATABASE_URL=postgresql://todouser:todopassword@postgres:5432/tododb
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:3000"]

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-auth-secret-here
"""

            root_env_example.write_text(root_env_content, encoding="utf-8")
            artifacts.append(str(root_env_example))

            # Create actual .env if it doesn't exist
            root_env = Path(".env")
            if not root_env.exists():
                root_env.write_text(root_env_content, encoding="utf-8")
                artifacts.append(str(root_env))

            # Create environment-specific documentation
            env_doc_path = Path("docs") / "environment-setup.md"
            env_doc_path.parent.mkdir(parents=True, exist_ok=True)

            env_doc_content = f"""# Environment Setup Guide

## Overview

This application uses environment variables for configuration across different environments.

## Environment Files

### Development

- **Backend**: `backend/.env`
- **Frontend**: `frontend/.env.local`
- **Docker Compose**: `.env` (root directory)

### Configuration Steps

1. **Copy example files**:
   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend
   cp frontend/.env.example frontend/.env.local

   # Docker Compose
   cp .env.example .env
   ```

2. **Update values**:
   - Replace placeholder values with actual secrets
   - Update DATABASE_URL for your database
   - Generate secure SECRET_KEY and BETTER_AUTH_SECRET

### Key Variables

#### Backend (`backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["http://localhost:3000"]` |
| `ACCESS_TOKEN_EXPIRE_HOURS` | JWT token expiry | `24` |

#### Frontend (`frontend/.env.local`)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_URL` | Frontend app URL | `http://localhost:3000` |
| `BETTER_AUTH_SECRET` | Auth secret key | `openssl rand -hex 32` |

## Security Best Practices

1. **Never commit `.env` files** - They contain secrets
2. **Use different secrets per environment**
3. **Rotate secrets regularly**
4. **Use secrets management in production** (AWS Secrets Manager, etc.)
5. **Limit CORS origins in production**

## Generating Secrets

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate BETTER_AUTH_SECRET
openssl rand -hex 32
```

## Environment: {environment}

Current environment configuration is set for **{environment}**.

## Troubleshooting

### Database connection issues
- Verify DATABASE_URL format
- Check database is running
- Verify credentials and network access

### CORS errors
- Verify ALLOWED_ORIGINS includes frontend URL
- Check protocol (http vs https)
- Ensure no trailing slashes

### Authentication errors
- Verify SECRET_KEY matches across services
- Check BETTER_AUTH_SECRET is set
- Verify token expiration settings
"""

            env_doc_path.write_text(env_doc_content, encoding="utf-8")
            artifacts.append(str(env_doc_path))

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "env_files_created": artifacts
                },
                artifacts=artifacts,
                logs=[f"Created {len(artifacts)} environment files"]
            )

        except Exception as e:
            self.logger.exception("Failed to configure environment variables")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            ".env.example files created for backend and frontend",
            "Actual .env files created if not existing",
            "All required variables documented",
            "Placeholder values provided",
            "Security notes included",
            "Environment-specific documentation created",
            "Variable descriptions clear",
            "Secrets generation instructions provided"
        ]
