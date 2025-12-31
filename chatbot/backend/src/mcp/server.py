"""
MCP Server using official MCP SDK.

Implements the Model Context Protocol to expose task operations as tools.
"""
from mcp.server import Server
from mcp.types import Tool, ArgumentsSchema
from pydantic import BaseModel
from typing import Any, Dict
import asyncio

from .tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
)

# Create MCP server instance
server = Server("todo-mcp-server")

# Register MCP tools using the official SDK
@server.tool(
    "add_task",
    description="Create a new task",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID who owns the task"},
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Optional task description"}
        },
        "required": ["user_id", "title"]
    }
)
async def handle_add_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle add_task requests via MCP protocol."""
    try:
        # Validate required parameters
        user_id = params["user_id"]
        title = params["title"]
        description = params.get("description")

        # Call the actual tool function
        from .tools.add_task import add_task
        result = add_task(user_id, title, description)
        return result
    except Exception as e:
        return {
            "task_id": None,
            "status": "error",
            "title": None,
            "error": str(e)
        }


@server.tool(
    "list_tasks",
    description="Retrieve tasks from the list",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID"},
            "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter by completion status"}
        },
        "required": ["user_id"]
    }
)
async def handle_list_tasks(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list_tasks requests via MCP protocol."""
    try:
        # Validate required parameters
        user_id = params["user_id"]
        status = params.get("status", "all")

        # Call the actual tool function
        from .tools.list_tasks import list_tasks
        result = list_tasks(user_id, status)
        return result
    except Exception as e:
        return {
            "tasks": [],
            "count": 0,
            "error": str(e)
        }


@server.tool(
    "complete_task",
    description="Mark a task as complete",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID who owns the task"},
            "task_id": {"type": "integer", "description": "Task ID to mark complete"}
        },
        "required": ["user_id", "task_id"]
    }
)
async def handle_complete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle complete_task requests via MCP protocol."""
    try:
        # Validate required parameters
        user_id = params["user_id"]
        task_id = params["task_id"]

        # Call the actual tool function
        from .tools.complete_task import complete_task
        result = complete_task(user_id, task_id)
        return result
    except Exception as e:
        return {
            "task_id": params.get("task_id"),
            "status": "error",
            "title": None,
            "error": str(e)
        }


@server.tool(
    "delete_task",
    description="Remove a task from the list",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID who owns the task"},
            "task_id": {"type": "integer", "description": "Task ID to delete"}
        },
        "required": ["user_id", "task_id"]
    }
)
async def handle_delete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle delete_task requests via MCP protocol."""
    try:
        # Validate required parameters
        user_id = params["user_id"]
        task_id = params["task_id"]

        # Call the actual tool function
        from .tools.delete_task import delete_task
        result = delete_task(user_id, task_id)
        return result
    except Exception as e:
        return {
            "task_id": params.get("task_id"),
            "status": "error",
            "title": None,
            "error": str(e)
        }


@server.tool(
    "update_task",
    description="Modify task title or description",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID who owns the task"},
            "task_id": {"type": "integer", "description": "Task ID to update"},
            "title": {"type": "string", "description": "New task title"},
            "description": {"type": "string", "description": "New task description"}
        },
        "required": ["user_id", "task_id"]
    }
)
async def handle_update_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle update_task requests via MCP protocol."""
    try:
        # Validate required parameters
        user_id = params["user_id"]
        task_id = params["task_id"]
        title = params.get("title")
        description = params.get("description")

        # Call the actual tool function
        from .tools.update_task import update_task
        result = update_task(user_id, task_id, title, description)
        return result
    except Exception as e:
        return {
            "task_id": params.get("task_id"),
            "status": "error",
            "title": None,
            "error": str(e)
        }


def get_mcp_server():
    """Get the MCP server instance."""
    return server


__all__ = [
    "server",
    "get_mcp_server",
]
