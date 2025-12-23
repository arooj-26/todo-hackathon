"""
E2E test for task creation flow.

Tests the complete flow: user sends message → agent interprets → tool is called → task is created.
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock

from src.mcp.tools.add_task import AddTaskParams
from src.mcp.tools.list_tasks import ListTasksParams
from src.agent.chat_agent import run_agent
from src.mcp.server import TOOLS


class TestTaskCreationE2E:
    """E2E tests for task creation through conversation."""

    def test_create_task_via_natural_language(self, engine):
        """Test creating a task through natural language."""
        # Mock OpenAI client
        with patch('src.agent.chat_agent.client') as mock_client:
            # Setup mock response for OpenAI
            mock_completion = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "I've added 'Buy groceries' to your tasks!"
            mock_message.tool_calls = [
                MagicMock(
                    function=MagicMock(
                        name="add_task",
                        arguments='{"title": "Buy groceries", "description": null, "priority": "medium", "due_date": null}'
                    )
                )
            ]
            mock_completion.choices = [MagicMock(message=mock_message)]
            mock_client.chat.completions.create.return_value = mock_completion

            # Run agent with natural language
            user_id = str(uuid4())
            messages = [{"role": "user", "content": "Add buy groceries to my list"}]

            with patch('src.mcp.tools.add_task.engine', engine), \
                 patch('src.mcp.tools.list_tasks.engine', engine):

                response = run_agent(messages, user_id)

                # Verify response structure
                assert response["response"] is not None
                assert response["error"] is None
                assert len(response["tool_calls"]) > 0

                # Verify task was created
                tool_call = response["tool_calls"][0]
                assert tool_call["tool"] == "add_task"
                assert tool_call["result"]["status"] == "created"
                assert "groceries" in tool_call["result"]["title"].lower()

    def test_list_tasks_after_creation(self, engine):
        """Test listing tasks after creating them."""
        from src.mcp.tools.add_task import add_task
        from src.mcp.tools.list_tasks import list_tasks

        with patch('src.mcp.tools.add_task.engine', engine), \
             patch('src.mcp.tools.list_tasks.engine', engine):

            user_id = uuid4()

            # Create two tasks
            add_task(AddTaskParams(user_id=user_id, title="Task 1"))
            add_task(AddTaskParams(user_id=user_id, title="Task 2"))

            # List tasks
            result = list_tasks(ListTasksParams(user_id=user_id))

            assert result["count"] == 2
            assert len(result["tasks"]) == 2
            assert result["error"] is None
