"""
BackendDeveloper_Agent

Specialized agent for FastAPI backend development.
Handles API endpoints, authentication, and business logic.
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


class BackendDeveloperAgent(Agent):
    """Agent responsible for backend development."""

    @property
    def config(self) -> AgentConfig:
        """Return agent configuration."""
        return AgentConfig(
            metadata=AgentMetadata(
                agent_id="BACKEND-001",
                name="BackendDeveloper",
                domain="FastAPI backend, API endpoints, business logic",
                description="Implements FastAPI application with API endpoints, JWT authentication, and business logic",
                version="1.0.0",
                autonomy_level="high",
                skills=[
                    "BE-001",  # Initialize FastAPI Project
                    "BE-002",  # Define API Endpoint
                    "BE-003",  # Implement JWT Authentication
                    "BE-004",  # Configure CORS
                    "BE-005",  # Implement User-Scoped Data Access
                    "AUTH-001",  # Hash Password
                    "AUTH-002",  # Verify User Credentials
                    "AUTH-003",  # Validate JWT Token
                    "TEST-001",  # Write Backend Unit Test
                    "TEST-002",  # Write API Integration Test
                    "DOC-001"   # Generate OpenAPI Schema
                ],
                dependencies=["DATABASE-001", "SPEC-001"]
            ),
            can_decide=[
                "API endpoint structure and naming",
                "Request/response schema design",
                "Error handling and status codes",
                "Input validation rules",
                "Business logic implementation",
                "Authentication flow details"
            ],
            must_consult=[
                "Database schema changes → Database agent",
                "New API requirements → SpecWriter agent",
                "CORS configuration changes → DevOps agent"
            ],
            cannot_decide=[
                "Database schema design",
                "Frontend UI/UX decisions",
                "Infrastructure configuration",
                "Deployment strategy"
            ],
            communication_protocols={
                "request_schema": {
                    "to_agent": "DATABASE-001",
                    "message_type": "request",
                    "topic": "schema_info",
                    "payload_schema": {
                        "model_name": "string"
                    }
                },
                "notify_api_ready": {
                    "to_agent": "FRONTEND-001",
                    "message_type": "notification",
                    "topic": "api_ready",
                    "payload_schema": {
                        "endpoints": "array",
                        "base_url": "string"
                    }
                }
            }
        )

    def plan_task(self, task: TaskAssignment) -> List[str]:
        """
        Plan how to accomplish a task.

        Analyzes the task and determines which skills to execute in what order.

        Args:
            task: Task assignment

        Returns:
            List of skill IDs to execute
        """
        skill_plan = []

        # Determine task type from description
        task_desc = task.description.lower()

        if "initialize" in task_desc or "setup" in task_desc:
            # Project setup tasks
            skill_plan.extend([
                "BE-001",  # Initialize FastAPI Project
                "BE-003",  # Implement JWT Authentication
                "BE-004",  # Configure CORS
                "BE-005"   # Implement User-Scoped Data Access
            ])

        elif "endpoint" in task_desc or "api" in task_desc:
            # API endpoint tasks
            skill_plan.extend([
                "BE-002",  # Define API Endpoint
                "TEST-002"  # Write API Integration Test
            ])

        elif "auth" in task_desc or "authentication" in task_desc:
            # Authentication tasks
            skill_plan.extend([
                "BE-003",  # Implement JWT Authentication
                "AUTH-001",  # Hash Password
                "AUTH-002",  # Verify User Credentials
                "AUTH-003",  # Validate JWT Token
                "TEST-002"  # Write API Integration Test
            ])

        elif "test" in task_desc:
            # Testing tasks
            skill_plan.extend([
                "TEST-001",  # Write Backend Unit Test
                "TEST-002"   # Write API Integration Test
            ])

        elif "documentation" in task_desc or "openapi" in task_desc:
            # Documentation tasks
            skill_plan.append("DOC-001")  # Generate OpenAPI Schema

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

            # Check if we can execute this skill
            if not self.can_execute_skill(skill_id):
                self.logger.error(f"Cannot execute skill: {skill_id}")
                results.append({
                    "skill_id": skill_id,
                    "status": "failed",
                    "error": "Skill not available to this agent"
                })
                continue

            # Get parameters for this skill from task inputs
            skill_params = task.inputs.get(skill_id, {})

            # Execute skill
            output = self.execute_skill(skill_id, skill_params)

            results.append({
                "skill_id": skill_id,
                "status": output.status.value,
                "result": output.result,
                "error": output.error,
                "artifacts": output.artifacts,
                "duration": output.duration
            })

            # If skill failed, stop execution
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

        # Notify other agents if task completed
        if task_status == "completed":
            # Notify Frontend agent that API is ready
            if "endpoint" in task.description.lower() or "api" in task.description.lower():
                self.send_message(
                    to_agent="FRONTEND-001",
                    message_type=MessageType.NOTIFICATION,
                    topic="api_ready",
                    payload={
                        "task_id": task.task_id,
                        "agent_id": self.config.metadata.agent_id,
                        "endpoints": [r.get("result", {}).get("router_path") for r in results if r.get("result")]
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
backend_agent = BackendDeveloperAgent()
register_agent(backend_agent)
