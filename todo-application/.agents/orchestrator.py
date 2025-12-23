"""
Multi-Agent Orchestrator

Coordinates multiple specialized agents to collaboratively implement features.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime
import uuid
from pathlib import Path

from .lib.agent_base import (
    Agent,
    TaskAssignment,
    AgentStatus,
    AgentMessage,
    MessageType,
    agent_registry
)


@dataclass
class WorkflowStep:
    """A step in a workflow."""
    step_id: str
    agent_id: str
    description: str
    skills_required: List[str]
    inputs: Dict[str, Any]
    depends_on: List[str]  # Step IDs this depends on
    priority: str = "normal"


@dataclass
class Workflow:
    """A workflow composed of multiple steps."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    created_at: str


class Orchestrator:
    """
    Multi-agent orchestrator.

    Coordinates multiple specialized agents to collaboratively complete workflows.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize orchestrator."""
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.workflows: Dict[str, Workflow] = {}
        self.completed_steps: List[str] = []
        self.failed_steps: List[str] = []
        self.active_tasks: Dict[str, TaskAssignment] = {}

    def create_workflow(self, name: str, description: str, steps: List[WorkflowStep]) -> str:
        """
        Create a new workflow.

        Args:
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps

        Returns:
            Workflow ID
        """
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=steps,
            created_at=datetime.now().isoformat()
        )

        self.workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow {workflow_id}: {name}")

        return workflow_id

    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow execution result
        """
        if workflow_id not in self.workflows:
            return {
                "status": "error",
                "error": f"Workflow not found: {workflow_id}"
            }

        workflow = self.workflows[workflow_id]
        self.logger.info(f"Executing workflow: {workflow.name}")

        # Track step execution results
        step_results = {}

        # Execute steps in dependency order
        remaining_steps = list(workflow.steps)
        max_iterations = len(remaining_steps) * 2  # Prevent infinite loops
        iteration = 0

        while remaining_steps and iteration < max_iterations:
            iteration += 1
            executed_in_iteration = False

            for step in list(remaining_steps):
                # Check if dependencies are met
                dependencies_met = all(
                    dep_id in self.completed_steps
                    for dep_id in step.depends_on
                )

                if not dependencies_met:
                    continue

                # Execute step
                self.logger.info(f"Executing step: {step.step_id} - {step.description}")

                result = self.execute_step(step)
                step_results[step.step_id] = result

                if result["status"] == "completed":
                    self.completed_steps.append(step.step_id)
                    executed_in_iteration = True
                elif result["status"] == "failed":
                    self.failed_steps.append(step.step_id)
                    self.logger.error(f"Step {step.step_id} failed: {result.get('error')}")

                    # Decide whether to continue or stop
                    if step.priority == "urgent":
                        # Stop workflow on urgent step failure
                        self.logger.error(f"Workflow stopped due to failed urgent step: {step.step_id}")
                        return {
                            "workflow_id": workflow_id,
                            "status": "failed",
                            "completed_steps": len(self.completed_steps),
                            "failed_steps": len(self.failed_steps),
                            "step_results": step_results
                        }

                remaining_steps.remove(step)

            if not executed_in_iteration:
                # No progress made - circular dependency or all remaining steps blocked
                self.logger.warning("No progress in iteration - circular dependency or blocked steps")
                break

        # Determine workflow status
        if not remaining_steps:
            workflow_status = "completed"
        elif self.failed_steps:
            workflow_status = "partial"
        else:
            workflow_status = "blocked"

        result = {
            "workflow_id": workflow_id,
            "status": workflow_status,
            "completed_steps": len(self.completed_steps),
            "failed_steps": len(self.failed_steps),
            "remaining_steps": len(remaining_steps),
            "step_results": step_results
        }

        self.logger.info(f"Workflow {workflow_id} completed with status: {workflow_status}")

        return result

    def execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute a workflow step.

        Args:
            step: Workflow step

        Returns:
            Step execution result
        """
        # Get agent from registry
        agent = agent_registry.get(step.agent_id)

        if not agent:
            return {
                "step_id": step.step_id,
                "status": "failed",
                "error": f"Agent not found: {step.agent_id}"
            }

        # Create task assignment
        task = TaskAssignment(
            task_id=step.step_id,
            description=step.description,
            skills_required=step.skills_required,
            inputs=step.inputs,
            priority=step.priority
        )

        # Track active task
        self.active_tasks[step.step_id] = task

        # Execute task
        try:
            result = agent.execute_task(task)

            # Remove from active tasks
            if step.step_id in self.active_tasks:
                del self.active_tasks[step.step_id]

            return result

        except Exception as e:
            self.logger.exception(f"Error executing step {step.step_id}")

            if step.step_id in self.active_tasks:
                del self.active_tasks[step.step_id]

            return {
                "step_id": step.step_id,
                "status": "failed",
                "error": str(e)
            }

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent status or None if not found
        """
        agent = agent_registry.get(agent_id)
        if agent:
            return agent.get_status()
        return None

    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all agents.

        Returns:
            List of agent statuses
        """
        return agent_registry.get_status_all()

    def create_feature_implementation_workflow(self) -> str:
        """
        Create a standard feature implementation workflow.

        Returns:
            Workflow ID
        """
        steps = [
            WorkflowStep(
                step_id="db-schema",
                agent_id="DATABASE-001",
                description="Define database schema for Task and User models",
                skills_required=["DB-001", "DB-002", "DB-004"],
                inputs={
                    "DB-001": {
                        "model_name": "User",
                        "fields": [
                            {"name": "id", "type": "int", "optional": True},
                            {"name": "email", "type": "str", "unique": True, "index": True},
                            {"name": "password_hash", "type": "str"},
                            {"name": "created_at", "type": "datetime"},
                            {"name": "updated_at", "type": "datetime"}
                        ]
                    }
                },
                depends_on=[],
                priority="urgent"
            ),
            WorkflowStep(
                step_id="backend-setup",
                agent_id="BACKEND-001",
                description="Initialize FastAPI project with authentication",
                skills_required=["BE-001", "BE-003", "BE-004", "BE-005"],
                inputs={
                    "BE-001": {"project_name": "backend"}
                },
                depends_on=["db-schema"],
                priority="urgent"
            ),
            WorkflowStep(
                step_id="frontend-setup",
                agent_id="FRONTEND-001",
                description="Initialize Next.js project with authentication",
                skills_required=["FE-001", "FE-003", "FE-004", "FE-005"],
                inputs={
                    "FE-001": {"project_name": "frontend"}
                },
                depends_on=["backend-setup"],
                priority="urgent"
            ),
            WorkflowStep(
                step_id="devops-setup",
                agent_id="DEVOPS-001",
                description="Configure Docker and environment variables",
                skills_required=["DEVOPS-001", "DEVOPS-002"],
                inputs={
                    "DEVOPS-001": {"include_postgres": True}
                },
                depends_on=["frontend-setup", "backend-setup"],
                priority="normal"
            )
        ]

        return self.create_workflow(
            name="Feature Implementation",
            description="Complete feature implementation with all agents",
            steps=steps
        )


def main():
    """Main entry point for orchestrator testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Import all agents to register them
    from .agents import (
        frontend_agent,
        backend_agent,
        database_agent,
        spec_writer_agent,
        devops_agent
    )

    orchestrator = Orchestrator()

    # Create and execute workflow
    workflow_id = orchestrator.create_feature_implementation_workflow()
    result = orchestrator.execute_workflow(workflow_id)

    print("\n" + "=" * 80)
    print("WORKFLOW EXECUTION COMPLETE")
    print("=" * 80)
    print(f"Status: {result['status']}")
    print(f"Completed Steps: {result['completed_steps']}")
    print(f"Failed Steps: {result['failed_steps']}")
    print(f"Remaining Steps: {result.get('remaining_steps', 0)}")
    print("\nAgent Status:")
    print("-" * 80)

    for agent_status in orchestrator.get_all_agents_status():
        print(f"{agent_status['agent_name']} ({agent_status['agent_id']}): {agent_status['status']}")
        print(f"  Completed: {agent_status['completed_tasks']}, Failed: {agent_status['failed_tasks']}")

    print("=" * 80)


if __name__ == "__main__":
    main()
