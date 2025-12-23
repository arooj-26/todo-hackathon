"""
DatabaseAdmin_Agent

Specialized agent for database schema and migrations.
Handles SQLModel definitions, Alembic migrations, and database optimization.
"""

from typing import Dict, List, Any
from pathlib import Path

from ..lib.agent_base import (
    Agent,
    AgentConfig,
    AgentMetadata,
    TaskAssignment,
    AgentStatus,
    MessageType,
    register_agent
)
from ..lib.skill_base import SkillStatus


class DatabaseAdminAgent(Agent):
    """Agent responsible for database administration."""

    @property
    def config(self) -> AgentConfig:
        """Return agent configuration."""
        return AgentConfig(
            metadata=AgentMetadata(
                agent_id="DATABASE-001",
                name="DatabaseAdmin",
                domain="Database schema, migrations, data access",
                description="Manages database schema with SQLModel, creates migrations with Alembic, and optimizes queries",
                version="1.0.0",
                autonomy_level="medium",  # Schema changes require approval
                skills=[
                    "DB-001",  # Define Database Schema
                    "DB-002",  # Connect to Neon Database
                    "DB-003",  # Create Database Migration
                    "DB-004"   # Create Database Indexes
                ],
                dependencies=["SPEC-001"]
            ),
            can_decide=[
                "Index creation for optimization",
                "Field types and constraints",
                "Database connection pool settings",
                "Migration script details"
            ],
            must_consult=[
                "New entity additions → SpecWriter agent",
                "Schema breaking changes → Backend agent",
                "Foreign key relationships → Backend agent"
            ],
            cannot_decide=[
                "Business logic and validation rules",
                "API contract definitions",
                "Frontend data requirements"
            ],
            communication_protocols={
                "schema_response": {
                    "to_agent": "BACKEND-001",
                    "message_type": "response",
                    "topic": "schema_info",
                    "payload_schema": {
                        "model_name": "string",
                        "fields": "array",
                        "relationships": "array"
                    }
                },
                "migration_notification": {
                    "to_agent": "broadcast",
                    "message_type": "notification",
                    "topic": "migration_created",
                    "payload_schema": {
                        "migration_file": "string",
                        "models_affected": "array"
                    }
                }
            }
        )

    def plan_task(self, task: TaskAssignment) -> List[str]:
        """
        Plan how to accomplish a task.

        Args:
            task: Task assignment

        Returns:
            List of skill IDs to execute
        """
        skill_plan = []

        task_desc = task.description.lower()

        if "initialize" in task_desc or "setup" in task_desc or "connect" in task_desc:
            # Database setup tasks
            skill_plan.extend([
                "DB-002",  # Connect to Neon Database
                "DB-001",  # Define Database Schema
                "DB-004",  # Create Database Indexes
                "DB-003"   # Create Database Migration
            ])

        elif "schema" in task_desc or "model" in task_desc:
            # Schema definition tasks
            skill_plan.extend([
                "DB-001",  # Define Database Schema
                "DB-004",  # Create Database Indexes
                "DB-003"   # Create Database Migration
            ])

        elif "migration" in task_desc or "migrate" in task_desc:
            # Migration tasks
            skill_plan.append("DB-003")  # Create Database Migration

        elif "index" in task_desc or "optimize" in task_desc or "performance" in task_desc:
            # Performance optimization tasks
            skill_plan.extend([
                "DB-004",  # Create Database Indexes
                "DB-003"   # Create Database Migration
            ])

        # Use explicitly required skills if specified
        if task.skills_required:
            skill_plan = task.skills_required

        self.logger.info(f"Planned {len(skill_plan)} skills for task: {task.task_id}")
        return skill_plan

    def execute_task(self, task: TaskAssignment) -> Dict[str, Any]:
        """
        Execute a task.

        Args:
            task: Task assignment

        Returns:
            Task execution result
        """
        self.current_task = task
        self.status = AgentStatus.WORKING

        self.logger.info(f"Starting task: {task.task_id} - {task.description}")

        # Plan the task
        skill_plan = self.plan_task(task)

        if not skill_plan:
            self.logger.warning("No skills planned for this task")
            self.status = AgentStatus.IDLE
            return {
                "task_id": task.task_id,
                "status": "skipped",
                "reason": "No applicable skills for this task"
            }

        # Execute skills in sequence
        results = []
        for skill_id in skill_plan:
            self.logger.info(f"Executing skill: {skill_id}")

            if not self.can_execute_skill(skill_id):
                self.logger.error(f"Cannot execute skill: {skill_id}")
                results.append({
                    "skill_id": skill_id,
                    "status": "failed",
                    "error": "Skill not available to this agent"
                })
                continue

            skill_params = task.inputs.get(skill_id, {})
            output = self.execute_skill(skill_id, skill_params)

            results.append({
                "skill_id": skill_id,
                "status": output.status.value,
                "result": output.result,
                "error": output.error,
                "artifacts": output.artifacts,
                "duration": output.duration
            })

            if output.status == SkillStatus.FAILED:
                self.logger.error(f"Skill {skill_id} failed: {output.error}")
                break

        # Determine overall task status
        all_succeeded = all(r["status"] == "success" for r in results)
        any_failed = any(r["status"] == "failed" for r in results)

        if all_succeeded:
            task_status = "completed"
            self.completed_tasks.append(task.task_id)
        elif any_failed:
            task_status = "failed"
            self.failed_tasks.append(task.task_id)
        else:
            task_status = "partial"

        self.status = AgentStatus.IDLE
        self.current_task = None

        result = {
            "task_id": task.task_id,
            "status": task_status,
            "skills_executed": len(results),
            "results": results
        }

        self.logger.info(f"Task {task.task_id} completed with status: {task_status}")

        # Notify other agents
        if task_status == "completed":
            # If migration was created, notify all agents
            migration_results = [r for r in results if r["skill_id"] == "DB-003"]
            if migration_results:
                self.send_message(
                    to_agent="broadcast",
                    message_type=MessageType.NOTIFICATION,
                    topic="migration_created",
                    payload={
                        "task_id": task.task_id,
                        "agent_id": self.config.metadata.agent_id,
                        "migration_file": migration_results[0].get("result", {}).get("migration_file"),
                        "models_affected": [r.get("result", {}).get("model_name") for r in results if r.get("result", {}).get("model_name")]
                    }
                )

            # Notify SpecWriter
            self.send_message(
                to_agent="SPEC-001",
                message_type=MessageType.NOTIFICATION,
                topic="task_completed",
                payload={
                    "task_id": task.task_id,
                    "agent_id": self.config.metadata.agent_id,
                    "artifacts": [a for r in results if r.get("artifacts") for a in r["artifacts"]]
                }
            )

        return result


# Create and register the agent
database_agent = DatabaseAdminAgent()
register_agent(database_agent)
