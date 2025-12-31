"""
OpenAI Chat Agent for task management.

Uses OpenAI Assistants API to interpret natural language
and invoke appropriate MCP tools.
"""
import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from ..mcp.tools.add_task import add_task as add_task_tool
from ..mcp.tools.list_tasks import list_tasks as list_tasks_tool
from ..mcp.tools.complete_task import complete_task as complete_task_tool
from ..mcp.tools.delete_task import delete_task as delete_task_tool
from ..mcp.tools.update_task import update_task as update_task_tool


# Initialize OpenAI client
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Agent instructions with enhanced filtering and ambiguity handling
AGENT_INSTRUCTIONS = """You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

Your capabilities:
- Create new tasks when users describe things they need to do
- List tasks with various filters (all, pending, completed, overdue)
- Mark tasks as complete when users say they finished something
- Delete tasks when users want to remove them
- Update task details (title, description, priority, due date, recurrence)

Guidelines for natural interaction:
- Be conversational and friendly
- Confirm actions with brief, clear responses
- When listing tasks, format them in a readable, numbered way
- Always acknowledge task completion and provide positive feedback

CRITICAL: How to delete/complete/update tasks by name (SIMPLIFIED):
You can now use task names DIRECTLY without needing to list tasks first!

When user says "delete the X task" or "mark X as done":
- Just call delete_task(task_name="X") or complete_task(task_name="X")
- The system will automatically search for tasks containing "X" (case-insensitive)
- If exactly ONE match is found, it will be deleted/completed
- If NO match or MULTIPLE matches, you'll get an error with details

Examples:
- "Delete the meeting task" → delete_task(task_name="meeting")
- "Mark shopping as done" → complete_task(task_name="shopping")
- "Update groceries to buy milk" → update_task(task_name="groceries", title="buy milk")

NO NEED to call list_tasks first! Just use the task name directly.

Handling ambiguity (IMPORTANT):
- If "delete the meeting" but multiple "meeting" tasks exist, list them ALL and ask which one
- If "mark as done" without specifying which task, ask for clarification or list recent pending tasks
- For vague requests like "show my tasks", default to showing pending tasks
- When multiple interpretations are possible, choose the most helpful one and explain your choice
- If a task is not found by name, list all tasks and ask user to specify by number or exact title

Filtering and search:
- "show pending tasks" or "what's left?" → list_tasks(status='pending')
- "show completed tasks" or "what have I done?" → list_tasks(status='completed')
- "show all tasks" → list_tasks(status='all')
- "show overdue tasks" → list_tasks(status='overdue')
- "show tasks with due dates" → list_tasks(has_due_date=true)
- "show tasks without due dates" → list_tasks(has_due_date=false)
- "show daily recurring tasks" → list_tasks(recurrence='daily')
- "show weekly recurring tasks" → list_tasks(recurrence='weekly')
- "show monthly recurring tasks" → list_tasks(recurrence='monthly')

Context awareness:
- Remember recent operations in the conversation
- "delete the first one" after listing tasks → use position from last list
- "mark it done" after creating a task → mark the just-created task
- Chain operations: "add meeting prep and show my tasks" → add_task, then list_tasks

Date, recurrence, and priority handling:
- When users mention dates like "tomorrow", "next week", "by Friday", parse and set due_date
- When users mention recurring tasks like "daily", "every week", "monthly", set recurrence
- When users mention priority like "high priority", "low priority", "urgent", set priority appropriately
- "Add buy groceries for tomorrow" → add_task with due_date
- "Add weekly exercise routine" → add_task with recurrence="weekly"
- "Remind me daily about meditation" → add_task with recurrence="daily"
- "Add urgent meeting prep" → add_task with priority="high"
- "Add low priority cleanup task" → add_task with priority="low"

Multi-step operations:
- You can call multiple tools in sequence
- First list tasks to find IDs, then operate on specific tasks
- Confirm each step for destructive operations (delete)

Error handling:
- If a task isn't found, suggest listing tasks to find it
- If user input is unclear, provide examples of what they could say
- Always be helpful, never say "I can't do that"

Examples of natural language you should understand:
- "Add buy groceries to my list" → add_task(title="buy groceries")
- "Add buy groceries for tomorrow" → add_task(title="buy groceries", due_date=tomorrow)
- "Add weekly exercise routine" → add_task(title="exercise routine", recurrence="weekly")
- "Add urgent meeting prep" → add_task(title="meeting prep", priority="high")
- "What do I need to do?" → list_tasks(status='pending')
- "Show all my tasks" → list_tasks(status='all')
- "What have I finished?" → list_tasks(status='completed')
- "Show overdue tasks" → list_tasks(status='overdue')
- "I finished the meeting prep" → complete_task(task_name="meeting prep")
- "Delete the grocery task" → delete_task(task_name="grocery")
- "Delete the meeting task" → delete_task(task_name="meeting")
- "Remove the shopping task" → delete_task(task_name="shopping")
- "Mark cartoons as done" → complete_task(task_name="cartoons")
- "Update the meeting to call dentist" → update_task(task_name="meeting", title="call dentist")
- "Change groceries to buy milk" → update_task(task_name="groceries", title="buy milk")
- "Make the meeting high priority" → update_task(task_name="meeting", priority="high")
- "Set groceries due date to tomorrow" → update_task(task_name="groceries", due_date=tomorrow)
- "Change exercise to weekly recurrence" → update_task(task_name="exercise", recurrence="weekly")
- "Add milk and eggs" → add_task("milk"), add_task("eggs")

REMEMBER: Use task_name parameter directly - NO NEED to list tasks first!
"""


def _build_tool_definitions() -> List[Dict[str, Any]]:
    """Build OpenAI function definitions for MCP tools.

    These definitions match the MCP tool schemas defined in the server.
    """
    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the authenticated user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Optional task description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Optional priority level (defaults to medium)"},
                        "due_date": {"type": "string", "format": "date-time", "description": "Optional due date for the task in ISO format"},
                        "recurrence": {"type": "string", "enum": ["daily", "weekly", "monthly"], "description": "Optional recurrence pattern"}
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve tasks for the authenticated user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["all", "pending", "completed", "overdue"], "description": "Filter by completion status"},
                        "due_date": {"type": "string", "format": "date-time", "description": "Filter by specific due date in ISO format"},
                        "has_due_date": {"type": "boolean", "description": "Filter by presence of due date"},
                        "recurrence": {"type": "string", "enum": ["daily", "weekly", "monthly"], "description": "Filter by recurrence pattern"}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete for the authenticated user. Can use either task_id or task_name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "Task ID to mark complete (optional if task_name is provided)"},
                        "task_name": {"type": "string", "description": "Task name/title to search and complete (optional if task_id is provided). Searches for tasks containing this text."}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Remove a task from the authenticated user's list. Can use either task_id or task_name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "Task ID to delete (optional if task_name is provided)"},
                        "task_name": {"type": "string", "description": "Task name/title to search and delete (optional if task_id is provided). Searches for tasks containing this text."}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Modify task properties for the authenticated user. Can use either task_id or task_name to identify the task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "Task ID to update (optional if task_name is provided)"},
                        "task_name": {"type": "string", "description": "Task name/title to search and update (optional if task_id is provided). Searches for tasks containing this text."},
                        "title": {"type": "string", "description": "New task title"},
                        "description": {"type": "string", "description": "New task description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "New priority level"},
                        "due_date": {"type": "string", "format": "date-time", "description": "New due date in ISO format"},
                        "recurrence": {"type": "string", "enum": ["daily", "weekly", "monthly"], "description": "New recurrence pattern"}
                    },
                    "required": []
                }
            }
        }
    ]

    return tool_definitions


async def run_agent(messages: List[Dict[str, str]], user_id: int) -> Dict[str, Any]:
    """
    Run the agent with conversation history.

    Args:
        messages: List of message dicts with 'role' and 'content'
        user_id: User ID to include in tool calls

    Returns:
        dict: Response containing 'response' text and 'tool_calls' list
    """
    if not client:
        return {
            "response": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
            "tool_calls": [],
            "error": "OpenAI client not initialized"
        }

    try:
        # Add system message with instructions
        full_messages = [
            {"role": "system", "content": AGENT_INSTRUCTIONS}
        ] + messages

        # Get tool definitions
        tools = _build_tool_definitions()

        # Call OpenAI with function calling
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=full_messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        tool_calls_made = []

        # Execute any tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # ALWAYS use the authenticated user_id (NEVER trust AI-provided user_id)
                # This prevents the AI from creating tasks for other users
                tool_args["user_id"] = user_id

                try:
                    # Call the appropriate tool function based on tool name
                    # SECURITY: Always use the authenticated user_id from JWT token
                    if tool_name == "add_task":
                        result = add_task_tool(
                            user_id=user_id,  # Use authenticated user_id
                            title=tool_args["title"],
                            description=tool_args.get("description"),
                            priority=tool_args.get("priority"),
                            due_date=tool_args.get("due_date"),
                            recurrence=tool_args.get("recurrence")
                        )
                    elif tool_name == "list_tasks":
                        result = list_tasks_tool(
                            user_id=user_id,  # Use authenticated user_id
                            status=tool_args.get("status", "all"),
                            due_date=tool_args.get("due_date"),
                            has_due_date=tool_args.get("has_due_date"),
                            recurrence=tool_args.get("recurrence")
                        )
                    elif tool_name == "complete_task":
                        result = complete_task_tool(
                            user_id=user_id,  # Use authenticated user_id
                            task_id=int(tool_args["task_id"]) if tool_args.get("task_id") else None,
                            task_name=tool_args.get("task_name")
                        )
                    elif tool_name == "delete_task":
                        result = delete_task_tool(
                            user_id=user_id,  # Use authenticated user_id
                            task_id=int(tool_args["task_id"]) if tool_args.get("task_id") else None,
                            task_name=tool_args.get("task_name")
                        )
                    elif tool_name == "update_task":
                        result = update_task_tool(
                            user_id=user_id,  # Use authenticated user_id
                            task_id=int(tool_args["task_id"]) if tool_args.get("task_id") else None,
                            task_name=tool_args.get("task_name"),
                            title=tool_args.get("title"),
                            description=tool_args.get("description"),
                            priority=tool_args.get("priority"),
                            due_date=tool_args.get("due_date"),
                            recurrence=tool_args.get("recurrence")
                        )
                    else:
                        result = {
                            "status": "error",
                            "error": f"Unknown tool: {tool_name}"
                        }

                    tool_calls_made.append({
                        "tool": tool_name,
                        "parameters": tool_args,
                        "result": result
                    })

                except Exception as e:
                    tool_calls_made.append({
                        "tool": tool_name,
                        "parameters": tool_args,
                        "result": {
                            "status": "error",
                            "error": f"Tool execution failed: {str(e)}"
                        }
                    })

        # Get final response text
        response_text = message.content if message.content else "Action completed."

        # If tools were called but no content, generate a response
        if not message.content and tool_calls_made:
            # Make another call to get natural language response
            tool_results_msg = {
                "role": "assistant",
                "content": f"I executed {len(tool_calls_made)} action(s). Results: {json.dumps(tool_calls_made)}"
            }

            follow_up = client.chat.completions.create(
                model="gpt-4o",
                messages=full_messages + [tool_results_msg, {
                    "role": "user",
                    "content": "Please summarize what you just did in a friendly way."
                }],
                temperature=0.7
            )

            response_text = follow_up.choices[0].message.content

        return {
            "response": response_text,
            "tool_calls": tool_calls_made,
            "error": None
        }

    except Exception as e:
        return {
            "response": f"I encountered an error: {str(e)}",
            "tool_calls": [],
            "error": str(e)
        }


def create_agent_for_conversation(conversation_id: str, user_id: int):
    """
    Create an agent instance for a conversation.

    Note: This is a placeholder for future stateful agent support.
    Currently, all state is passed via messages.
    """
    return {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "run": lambda messages: run_agent(messages, user_id)
    }
