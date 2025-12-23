"""
DevOps_Agent

Specialized agent for environment and deployment configuration.
Handles Docker, environment variables, and deployment documentation.
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


class DevOpsAgent(Agent):
    """Agent responsible for DevOps and deployment."""

    @property
    def config(self) -> AgentConfig:
        """Return agent configuration."""
        return AgentConfig(
            metadata=AgentMetadata(
                agent_id="DEVOPS-001",
                name="DevOps",
                domain="Environment, deployment, infrastructure",
                description="Configures Docker, environment variables, secrets, and deployment documentation",
                version="1.0.0",
                autonomy_level="medium",  # Infrastructure with oversight
                skills=[
                    "DEVOPS-001",  # Create Docker Compose Configuration
                    "DEVOPS-002"   # Configure Environment Variables
                ],
                dependencies=["BACKEND-001", "FRONTEND-001"]
            ),
            can_decide=[
                "Docker compose service configuration",
                "Environment variable naming",
                "Port mappings",
                "Volume mount strategies",
                "Container resource limits"
            ],
            must_consult=[
                "Production deployment → Team Lead",
                "Security credentials → Security team",
                "Infrastructure changes → Backend/Frontend agents",
                "Database connection strings → Database agent"
            ],
            cannot_decide=[
                "Production secrets values",
                "Cloud provider selection",
                "Scaling strategies",
                "CI/CD pipeline design"
            ],
            communication_protocols={
                "env_config_ready": {
                    "to_agent": "broadcast",
                    "message_type": "notification",
                    "topic": "env_configured",
                    "payload_schema": {
                        "env_files": "array",
                        "environment": "string"
                    }
                },
                "request_env_vars": {
                    "to_agent": "BACKEND-001",
                    "message_type": "request",
                    "topic": "required_env_vars",
                    "payload_schema": {
                        "service": "string"
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

        if "initialize" in task_desc or "setup" in task_desc:
            # Full environment setup
            skill_plan.extend([
                "DEVOPS-002",  # Configure Environment Variables
                "DEVOPS-001"   # Create Docker Compose Configuration
            ])

        elif "docker" in task_desc or "container" in task_desc:
            # Docker configuration tasks
            skill_plan.append("DEVOPS-001")  # Create Docker Compose Configuration

        elif "env" in task_desc or "environment" in task_desc or "config" in task_desc:
            # Environment variable tasks
            skill_plan.append("DEVOPS-002")  # Configure Environment Variables

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
            # If environment configured, notify all agents
            env_results = [r for r in results if r["skill_id"] == "DEVOPS-002"]
            if env_results:
                self.send_message(
                    to_agent="broadcast",
                    message_type=MessageType.NOTIFICATION,
                    topic="env_configured",
                    payload={
                        "task_id": task.task_id,
                        "agent_id": self.config.metadata.agent_id,
                        "env_files": env_results[0].get("result", {}).get("env_files_created", [])
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
devops_agent = DevOpsAgent()
register_agent(devops_agent)
