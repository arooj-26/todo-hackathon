"""
SpecWriter_Agent

Specialized agent for specifications and documentation.
Handles feature specs, API contracts, and documentation updates.
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


class SpecWriterAgent(Agent):
    """Agent responsible for specifications and documentation."""

    @property
    def config(self) -> AgentConfig:
        """Return agent configuration."""
        return AgentConfig(
            metadata=AgentMetadata(
                agent_id="SPEC-001",
                name="SpecWriter",
                domain="Specifications, documentation, requirements",
                description="Creates and maintains feature specifications, API contracts, and project documentation",
                version="1.0.0",
                autonomy_level="medium",  # Gatekeeper for requirements
                skills=[
                    "DOC-002"  # Update Specification Document
                ],
                dependencies=[]  # No dependencies - SpecWriter is the source of truth
            ),
            can_decide=[
                "Documentation structure and format",
                "Specification template usage",
                "API contract documentation",
                "Success criteria definitions"
            ],
            must_consult=[
                "New feature requirements → User/Product Owner",
                "Architecture changes → All technical agents",
                "Breaking API changes → Frontend and Backend agents"
            ],
            cannot_decide=[
                "Implementation details",
                "Technology choices",
                "Database schema design",
                "UI/UX implementation"
            ],
            communication_protocols={
                "clarification_request": {
                    "to_agent": "broadcast",
                    "message_type": "request",
                    "topic": "clarification",
                    "payload_schema": {
                        "question": "string",
                        "context": "string",
                        "blocking": "boolean"
                    }
                },
                "spec_updated": {
                    "to_agent": "broadcast",
                    "message_type": "notification",
                    "topic": "spec_updated",
                    "payload_schema": {
                        "spec_path": "string",
                        "section": "string",
                        "change_type": "string"
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

        # SpecWriter primarily uses DOC-002 for updating specifications
        if "update" in task_desc or "document" in task_desc or "spec" in task_desc:
            skill_plan.append("DOC-002")  # Update Specification Document

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

        # Notify other agents when spec is updated
        if task_status == "completed":
            for r in results:
                if r["skill_id"] == "DOC-002" and r.get("result"):
                    self.send_message(
                        to_agent="broadcast",
                        message_type=MessageType.NOTIFICATION,
                        topic="spec_updated",
                        payload={
                            "task_id": task.task_id,
                            "agent_id": self.config.metadata.agent_id,
                            "spec_path": r["result"].get("spec_path"),
                            "change_type": "update"
                        }
                    )

        return result

    def _handle_request(self, message) -> None:
        """Handle request messages from other agents."""
        if message.topic == "task_completed":
            # Track task completion for documentation
            self.logger.info(f"Task completed by {message.from_agent}: {message.payload.get('task_id')}")

            # Could update implementation status in spec
            # For now, just log it


# Create and register the agent
spec_writer_agent = SpecWriterAgent()
register_agent(spec_writer_agent)
