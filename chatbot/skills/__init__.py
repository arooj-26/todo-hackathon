"""
MCP Tools for Todo AI Chatbot

This package contains MCP (Model Context Protocol) server tools that expose
task management operations to the AI agent.

Available Tools:
- add_task: Create a new todo task
- list_tasks: Retrieve tasks with filters and sorting
- complete_task: Mark a task as complete
- delete_task: Permanently remove a task
- update_task: Modify task attributes

All tools use Pydantic validation and UUID-based identification for type safety.
"""

from .add_task import add_task, AddTaskParams, Priority
from .list_tasks import list_tasks, ListTasksParams, TaskStatus, SortBy
from .complete_task import complete_task, CompleteTaskParams
from .delete_task import delete_task, DeleteTaskParams
from .update_task import update_task, UpdateTaskParams

__all__ = [
    # Functions
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
    # Parameter Models
    "AddTaskParams",
    "ListTasksParams",
    "CompleteTaskParams",
    "DeleteTaskParams",
    "UpdateTaskParams",
    # Enums
    "Priority",
    "TaskStatus",
    "SortBy",
]
