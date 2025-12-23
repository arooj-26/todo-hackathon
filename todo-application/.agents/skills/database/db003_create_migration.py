"""
Skill DB-003: Create Database Migration

Creates Alembic migration scripts for database schema changes.
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
class CreateDatabaseMigrationSkill(Skill):
    """Create Alembic database migration."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="DB-003",
            name="Create Database Migration",
            description="Create Alembic migration scripts for database schema changes",
            category="database",
            version="1.0.0",
            dependencies=["BE-001", "DB-001"],
            inputs_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "autogenerate": {"type": "boolean", "default": True}
                },
                "required": ["message"]
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "migration_file": {"type": "string"},
                    "revision_id": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        params = inputs.params

        if "message" not in params:
            return False, "Missing required parameter: message"

        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        params = inputs.params
        message = params["message"]
        autogenerate = params.get("autogenerate", True)

        try:
            backend_path = Path("backend")
            alembic_dir = backend_path / "alembic"

            # Initialize Alembic if not already done
            if not alembic_dir.exists():
                self.logger.info("Initializing Alembic...")

                # Create alembic.ini
                alembic_ini_path = backend_path / "alembic.ini"
                alembic_ini_content = """# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

[alembic:exclude]
# Exclude tables from autogenerate
# exclude_tables = table1,table2

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
                alembic_ini_path.write_text(alembic_ini_content, encoding="utf-8")

                # Create alembic directory structure
                alembic_dir.mkdir(exist_ok=True)
                (alembic_dir / "versions").mkdir(exist_ok=True)

                # Create env.py
                env_py_path = alembic_dir / "env.py"
                env_py_content = """from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.config import settings
from app.db.base import *  # Import all models
from sqlmodel import SQLModel

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with our DATABASE_URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    \"\"\"Run migrations in 'offline' mode.\"\"\"
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    \"\"\"Run migrations in 'online' mode.\"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""
                env_py_path.write_text(env_py_content, encoding="utf-8")

                # Create script.py.mako template
                script_mako_path = alembic_dir / "script.py.mako"
                script_mako_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
                script_mako_path.write_text(script_mako_content, encoding="utf-8")

                self.logger.info("Alembic initialized successfully")

            # Create migration
            cmd = ["alembic", "revision"]
            if autogenerate:
                cmd.append("--autogenerate")
            cmd.extend(["-m", message])

            self.logger.info(f"Creating migration: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=backend_path,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                return SkillOutput(
                    status=SkillStatus.FAILED,
                    error=f"Migration failed: {result.stderr}",
                    logs=[result.stdout, result.stderr]
                )

            # Extract migration file path from output
            migration_file = None
            revision_id = None

            for line in result.stdout.split("\n"):
                if "Generating" in line:
                    # Extract file path
                    parts = line.split("...")
                    if len(parts) > 1:
                        migration_file = parts[1].strip()

            self.logger.info(f"Migration created: {migration_file}")

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "migration_file": migration_file or "unknown",
                    "revision_id": revision_id or "unknown"
                },
                artifacts=[str(alembic_ini_path), str(env_py_path)],
                logs=[result.stdout]
            )

        except Exception as e:
            self.logger.exception("Failed to create migration")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Alembic initialized (if first migration)",
            "alembic.ini configured",
            "env.py imports all models",
            "Migration file generated in versions/",
            "upgrade() function contains changes",
            "downgrade() function contains rollback",
            "Migration can be applied with 'alembic upgrade head'",
            "Migration can be rolled back with 'alembic downgrade -1'"
        ]
