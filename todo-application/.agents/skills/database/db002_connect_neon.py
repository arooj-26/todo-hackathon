"""
Skill DB-002: Connect to Neon Database

Configures database connection with connection pooling for Neon PostgreSQL.
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
class ConnectToNeonSkill(Skill):
    """Configure Neon database connection."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DB-002",
            name="Connect to Neon Database",
            description="Configure database connection with connection pooling for Neon PostgreSQL",
            category="database",
            version="1.0.0",
            dependencies=["BE-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "pool_size": {"type": "integer", "default": 10},
                    "max_overflow": {"type": "integer", "default": 20},
                    "pool_timeout": {"type": "integer", "default": 30}
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "session_module_path": {"type": "string"},
                    "configured": {"type": "boolean"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        pool_size = params.get("pool_size", 10)
        max_overflow = params.get("max_overflow", 20)
        pool_timeout = params.get("pool_timeout", 30)

        try:
            backend_path = Path("backend")
            db_path = backend_path / "app" / "db"

            # Create session.py
            session_path = db_path / "session.py"
            session_code = f"""from sqlmodel import Session, create_engine
from app.core.config import settings

# Create engine with connection pooling optimized for Neon
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_size={pool_size},  # Number of connections to maintain
    max_overflow={max_overflow},  # Maximum number of connections that can be created beyond pool_size
    pool_timeout={pool_timeout},  # Timeout for getting connection from pool
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={{
        "connect_timeout": 10,  # Connection timeout in seconds
        "options": "-c timezone=utc"  # Set timezone to UTC
    }}
)


def get_db():
    \"\"\"
    Dependency that provides a database session.

    Yields:
        Session: SQLModel database session

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.exec(select(Item)).all()
            return items
    \"\"\"
    with Session(engine) as session:
        yield session


def init_db():
    \"\"\"
    Initialize the database.

    Creates all tables defined in SQLModel models.
    Should be called on application startup.
    \"\"\"
    from sqlmodel import SQLModel
    from app.models import user, task  # Import all models

    SQLModel.metadata.create_all(engine)
"""

            session_path.write_text(session_code, encoding="utf-8")
            self.logger.info(f"Created session module: {session_path}")

            # Create base.py for model imports
            base_path = db_path / "base.py"
            base_code = """# Import all SQLModel models here so Alembic can detect them
from app.models.user import User
from app.models.task import Task

# This allows Alembic to auto-generate migrations
__all__ = ["User", "Task"]
"""

            base_path.write_text(base_code, encoding="utf-8")
            self.logger.info(f"Created base imports: {base_path}")

            # Update main.py to initialize database on startup
            main_py_path = backend_path / "app" / "main.py"
            if main_py_path.exists():
                main_content = main_py_path.read_text(encoding="utf-8")

                if "startup" not in main_content:
                    # Add startup event
                    startup_code = """

@app.on_event("startup")
def on_startup():
    \"\"\"Initialize database on application startup.\"\"\"
    from app.db.session import init_db
    init_db()
"""

                    # Insert before the root endpoint
                    if "@app.get(\"/\")" in main_content:
                        main_content = main_content.replace(
                            "@app.get(\"/\")",
                            startup_code + "\n\n@app.get(\"/\")"
                        )
                    else:
                        main_content += startup_code

                    main_py_path.write_text(main_content, encoding="utf-8")
                    self.logger.info("Added database initialization to startup")

            artifacts = [str(session_path), str(base_path)]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "session_module_path": str(session_path),
                    "configured": True
                },
                artifacts=artifacts,
                logs=[f"Configured Neon connection with pool_size={pool_size}"]
            )

        except Exception as e:
            self.logger.exception("Failed to configure Neon connection")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Database engine created with create_engine",
            "Connection pooling configured (pool_size, max_overflow)",
            "pool_pre_ping enabled for connection health checks",
            "pool_recycle set to prevent stale connections",
            "get_db dependency function created",
            "init_db function creates all tables",
            "Startup event initializes database",
            "Timezone set to UTC"
        ]
