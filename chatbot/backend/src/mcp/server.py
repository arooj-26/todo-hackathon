"""
MCP Server initialization.

Exports all MCP tools for the OpenAI Agent to use.
Note: Full MCP SDK integration can be added later if needed.
For now, tools are called directly by the agent.
"""
from .tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    AddTaskParams,
    ListTasksParams,
    CompleteTaskParams,
    DeleteTaskParams,
    UpdateTaskParams
)

# Tool registry for the agent to discover
TOOLS = {
    "add_task": {
        "function": add_task,
        "params_class": AddTaskParams,
        "description": "Create a new todo task for the user with a title and optional description, due date, and priority"
    },
    "list_tasks": {
        "function": list_tasks,
        "params_class": ListTasksParams,
        "description": "List todo tasks for the user with optional filters for completion status and priority, and sorting options"
    },
    "complete_task": {
        "function": complete_task,
        "params_class": CompleteTaskParams,
        "description": "Mark a todo task as complete by its ID"
    },
    "delete_task": {
        "function": delete_task,
        "params_class": DeleteTaskParams,
        "description": "Permanently delete a todo task by its ID"
    },
    "update_task": {
        "function": update_task,
        "params_class": UpdateTaskParams,
        "description": "Update a todo task's title, description, priority, or due date by its ID"
    }
}


def get_tool(tool_name: str):
    """Get a tool by name."""
    return TOOLS.get(tool_name)


def get_all_tools():
    """Get all available tools."""
    return TOOLS


__all__ = [
    "TOOLS",
    "get_tool",
    "get_all_tools",
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
]
