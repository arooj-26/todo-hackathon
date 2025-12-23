"""
OpenAI Chat Agent for task management.

Uses OpenAI's function calling to interpret natural language
and invoke appropriate MCP tools.
"""
import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from pydantic import ValidationError

from ..mcp.server import TOOLS


# Initialize OpenAI client
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Agent instructions with enhanced filtering and ambiguity handling
AGENT_INSTRUCTIONS = """You are a helpful task management assistant. You help users manage their todo tasks through natural conversation.

Your capabilities:
- Create new tasks when users describe things they need to do
- List tasks with various filters (all, pending, completed, by priority, by due date)
- Mark tasks as complete when users say they finished something
- Delete tasks when users want to remove them
- Update task details (title, description, priority, due date)

Guidelines for natural interaction:
- Be conversational and friendly
- Confirm actions with brief, clear responses
- When listing tasks, format them in a readable, numbered way
- Always acknowledge task completion and provide positive feedback

Handling ambiguity (IMPORTANT):
- If "delete the meeting" but multiple "meeting" tasks exist, list them and ask which one
- If "mark as done" without specifying which task, ask for clarification or list recent pending tasks
- For vague requests like "show my tasks", default to showing pending tasks
- When multiple interpretations are possible, choose the most helpful one and explain your choice

Filtering and search (User Story 3):
- "show pending tasks" or "what's left?" → list_tasks(status='pending')
- "show completed tasks" or "what have I done?" → list_tasks(status='completed')
- "show all tasks" → list_tasks(status='all')
- "show high priority tasks" or "what's urgent?" → list_tasks(priority='high')
- "what's due soon?" → list_tasks(sort_by='due_date')
- "show tasks by priority" → list_tasks(sort_by='priority')

Context awareness (User Story 4):
- Remember recent operations in the conversation
- "delete the first one" after listing tasks → use position from last list
- "mark it done" after creating a task → mark the just-created task
- Chain operations: "add meeting prep and show my tasks" → add_task, then list_tasks

Multi-step operations:
- You can call multiple tools in sequence
- First list tasks to find IDs, then operate on specific tasks
- Confirm each step for destructive operations (delete)

Error handling:
- If a task isn't found, suggest listing tasks to find it
- If user input is unclear, provide examples of what they could say
- Always be helpful, never say "I can't do that"

Examples of natural language you should understand:
- "Add buy groceries to my list" → add_task
- "Add buy milk with high priority" → add_task with priority='high'
- "What do I need to do?" → list_tasks(status='pending')
- "Show all my tasks" → list_tasks(status='all')
- "What have I finished?" → list_tasks(status='completed')
- "Show high priority items" → list_tasks(priority='high')
- "What's due soon?" → list_tasks(sort_by='due_date')
- "Mark task 1 as done" → complete_task (after listing to find ID)
- "I finished the meeting prep" → list tasks, find matching title, complete it
- "Delete the grocery task" → list tasks, find match, delete (or ask if multiple)
- "Change priority of task 2 to high" → update_task
- "Add milk and eggs" → add_task("milk"), add_task("eggs")
"""


def _build_tool_definitions() -> List[Dict[str, Any]]:
    """Build OpenAI function definitions from MCP tools."""
    tool_definitions = []

    for tool_name, tool_info in TOOLS.items():
        params_class = tool_info["params_class"]
        schema = params_class.model_json_schema()

        # Convert Pydantic schema to OpenAI function format
        function_def = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", [])
                }
            }
        }
        tool_definitions.append(function_def)

    return tool_definitions


def run_agent(messages: List[Dict[str, str]], user_id: str) -> Dict[str, Any]:
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

                # Inject user_id into tool arguments
                tool_args["user_id"] = user_id

                # Get tool from registry
                tool_info = TOOLS.get(tool_name)
                if tool_info:
                    tool_function = tool_info["function"]
                    params_class = tool_info["params_class"]

                    try:
                        # Validate and call tool
                        params = params_class(**tool_args)
                        result = tool_function(params)

                        tool_calls_made.append({
                            "tool": tool_name,
                            "parameters": tool_args,
                            "result": result
                        })

                    except ValidationError as e:
                        tool_calls_made.append({
                            "tool": tool_name,
                            "parameters": tool_args,
                            "result": {
                                "status": "error",
                                "error": f"Invalid parameters: {str(e)}"
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


def create_agent_for_conversation(conversation_id: str, user_id: str):
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
