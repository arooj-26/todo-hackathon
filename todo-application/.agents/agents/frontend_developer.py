"""
FrontendDeveloper_Agent

Specialized agent for Next.js frontend development.
Handles UI components, client-side logic, and frontend integration.
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


class FrontendDeveloperAgent(Agent):
    """Agent responsible for frontend development."""

    @property
    def config(self) -> AgentConfig:
        """Return agent configuration."""
        return AgentConfig(
            metadata=AgentMetadata(
                agent_id="FRONTEND-001",
                name="FrontendDeveloper",
                domain="Next.js frontend, React components, UI/UX",
                description="Implements Next.js application with App Router, React components, and frontend logic",
                version="1.0.0",
                autonomy_level="high",
                skills=[
                    "FE-001",  # Initialize Next.js Project
                    "FE-002",  # Create React Component
                    "FE-003",  # Implement Better Auth
                    "FE-004",  # Create API Client
                    "FE-005",  # Implement Route Protection
                    "FE-006",  # Style with TailwindCSS
                    "TEST-003"  # Write Frontend Component Test
                ],
                dependencies=["BACKEND-001", "SPEC-001"]
            ),
            can_decide=[
                "Component structure and organization",
                "State management approach (useState, useContext, etc.)",
                "CSS class application and styling details",
                "Client-side validation rules",
                "UI interaction patterns (loading states, error messages)",
                "Frontend routing structure"
            ],
            must_consult=[
                "API contract changes → Backend agent",
                "New route requirements → SpecWriter agent",
                "Authentication flow changes → Backend agent",
                "Environment variables → DevOps agent"
            ],
            cannot_decide=[
                "Backend API design",
                "Database schema changes",
                "Authentication token format",
                "CORS configuration"
            ],
            communication_protocols={
                "request_api_contract": {
                    "to_agent": "BACKEND-001",
                    "message_type": "request",
                    "topic": "api_contract",
                    "payload_schema": {
                        "endpoint": "string",
                        "method": "string"
                    }
                },
                "request_spec_clarification": {
                    "to_agent": "SPEC-001",
                    "message_type": "request",
                    "topic": "clarification",
                    "payload_schema": {
                        "question": "string",
                        "context": "string"
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
                "FE-001",  # Initialize Next.js Project
                "FE-003",  # Implement Better Auth
                "FE-004",  # Create API Client
                "FE-005"   # Implement Route Protection
            ])

        elif "component" in task_desc or "ui" in task_desc:
            # Component creation tasks
            skill_plan.extend([
                "FE-002",  # Create React Component
                "FE-006",  # Style with TailwindCSS
                "TEST-003"  # Write Component Test
            ])

        elif "auth" in task_desc or "signin" in task_desc or "signup" in task_desc:
            # Authentication tasks
            skill_plan.extend([
                "FE-003",  # Implement Better Auth
                "FE-002",  # Create auth components
                "FE-005",  # Implement Route Protection
                "FE-006"   # Style auth forms
            ])

        elif "api" in task_desc or "client" in task_desc:
            # API integration tasks
            skill_plan.append("FE-004")  # Create API Client

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

        # Notify SpecWriter if task completed
        if task_status == "completed":
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
frontend_agent = FrontendDeveloperAgent()
register_agent(frontend_agent)
