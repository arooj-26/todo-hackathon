# Task Name Feature - Delete/Update/Complete by Name

## Overview

The chatbot can now **delete, update, and complete tasks using their names directly** instead of requiring task IDs. This makes the chatbot much more natural and user-friendly!

## What Changed

### Before (Required IDs)
User: "Delete the meeting task"
Bot: *Lists all tasks, finds ID, then deletes*
Result: ❌ Two-step process, clunky

### After (Use Names Directly)
User: "Delete the meeting task"
Bot: *Immediately deletes the task*
Result: ✅ One-step process, natural!

## Updated Functions

### 1. `delete_task()`
**File**: `src/mcp/tools/delete_task.py`

**New Parameters**:
```python
def delete_task(
    user_id: int,
    task_id: int = None,        # Optional
    task_name: str = None       # New! Optional
) -> dict:
```

**Usage**:
- `delete_task(user_id=1, task_id=123)` - Delete by ID (old way)
- `delete_task(user_id=1, task_name="meeting")` - Delete by name (new way!)

**Features**:
- Case-insensitive partial matching
- If multiple matches found, returns error with list
- If no matches found, returns helpful error
- If exactly one match found, deletes it

### 2. `complete_task()`
**File**: `src/mcp/tools/complete_task.py`

**New Parameters**:
```python
def complete_task(
    user_id: int,
    task_id: int = None,        # Optional
    task_name: str = None       # New! Optional
) -> dict:
```

**Usage**:
- `complete_task(user_id=1, task_id=123)` - Complete by ID
- `complete_task(user_id=1, task_name="shopping")` - Complete by name!

**Features**:
- Only searches uncompleted tasks
- Same matching logic as delete_task
- Handles ambiguity gracefully

### 3. `update_task()`
**File**: `src/mcp/tools/update_task.py`

**New Parameters**:
```python
def update_task(
    user_id: int,
    task_id: int = None,        # Optional
    task_name: str = None,      # New! Optional
    title: str = None,
    description: str = None,
    due_date: datetime = None,
    recurrence: str = None
) -> dict:
```

**Usage**:
- `update_task(user_id=1, task_id=123, title="New title")` - Update by ID
- `update_task(user_id=1, task_name="groceries", title="Buy milk")` - Update by name!

**Features**:
- Find task by name, then update its properties
- Partial updates supported
- Same matching logic

## AI Agent Updates

### File: `src/agent/chat_agent.py`

**Updated Tool Definitions**:
All three tools now accept `task_name` as an optional parameter:

```python
{
    "name": "delete_task",
    "description": "Remove a task. Can use either task_id or task_name.",
    "parameters": {
        "task_id": "optional if task_name provided",
        "task_name": "optional if task_id provided"
    }
}
```

**Updated Instructions**:
The agent now knows it can use names directly:

```
CRITICAL: You can now use task names DIRECTLY!

When user says "delete the X task":
- Just call delete_task(task_name="X")
- NO NEED to call list_tasks first!

Examples:
- "Delete the meeting task" → delete_task(task_name="meeting")
- "Mark shopping as done" → complete_task(task_name="shopping")
- "Update groceries to buy milk" → update_task(task_name="groceries", title="buy milk")
```

## How It Works

### Search Algorithm

1. **Case-Insensitive Search**: Searches using `ILIKE` SQL operator
2. **Partial Match**: Finds tasks where description contains the search term
3. **Multiple Matches**: Returns error listing all matches
4. **No Matches**: Returns helpful "not found" error
5. **Single Match**: Proceeds with the operation

**Example Search**:
```python
# User has tasks: "Buy groceries", "Grocery shopping", "Meeting"
# User says: "Delete grocery"

# Search finds 2 matches:
# - "Buy groceries"
# - "Grocery shopping"

# Returns error:
{
    "status": "error",
    "error": "Multiple tasks found matching 'grocery': ID 1: Buy groceries, ID 2: Grocery shopping. Please specify which one."
}
```

## Natural Language Examples

### Delete Operations

| User Input | AI Action | Result |
|------------|-----------|--------|
| "Delete the meeting task" | `delete_task(task_name="meeting")` | ✅ Deletes if unique |
| "Remove shopping" | `delete_task(task_name="shopping")` | ✅ Deletes if unique |
| "Delete grocery" | `delete_task(task_name="grocery")` | ⚠️ Asks which one if multiple |

### Complete Operations

| User Input | AI Action | Result |
|------------|-----------|--------|
| "Mark meeting as done" | `complete_task(task_name="meeting")` | ✅ Completes if unique |
| "I finished shopping" | `complete_task(task_name="shopping")` | ✅ Completes if unique |
| "Complete cartoons" | `complete_task(task_name="cartoons")` | ✅ Completes if unique |

### Update Operations

| User Input | AI Action | Result |
|------------|-----------|--------|
| "Change meeting to call dentist" | `update_task(task_name="meeting", title="call dentist")` | ✅ Updates if unique |
| "Update groceries to buy milk" | `update_task(task_name="groceries", title="buy milk")` | ✅ Updates if unique |

## Error Handling

### No Matches Found
```json
{
    "status": "error",
    "error": "No task found with name containing 'xyz'"
}
```

**AI Response**: "I couldn't find a task with 'xyz' in the name. Let me show you all your tasks..."

### Multiple Matches
```json
{
    "status": "error",
    "error": "Multiple tasks found matching 'meeting': ID 5: Meeting at 2pm, ID 7: Team meeting. Please specify which one."
}
```

**AI Response**: Lists the tasks and asks user to be more specific.

### Task Successfully Deleted
```json
{
    "status": "deleted",
    "task_id": "5",
    "title": "meeting"
}
```

**AI Response**: "I've deleted the 'meeting' task."

## Benefits

### For Users
- ✅ More natural conversations
- ✅ Faster task operations
- ✅ No need to know task IDs
- ✅ Works like talking to a human

### For System
- ✅ Fewer API calls (no need to list first)
- ✅ Better performance
- ✅ Cleaner conversation flow
- ✅ Less token usage

## Testing

### Test Case 1: Delete by Name
```
User: "Delete the meeting task"
Expected: Task deleted if unique, or asks which one if multiple
```

### Test Case 2: Complete by Name
```
User: "Mark shopping as done"
Expected: Task completed if unique, or asks which one if multiple
```

### Test Case 3: Update by Name
```
User: "Change groceries to buy milk"
Expected: Task updated if unique, or asks which one if multiple
```

### Test Case 4: Ambiguous Name
```
User: "Delete meeting"
Tasks: "Meeting", "Team meeting", "Morning meeting"
Expected: AI lists all three and asks which one
```

### Test Case 5: Not Found
```
User: "Delete xyz"
Expected: "I couldn't find a task named 'xyz'"
```

## Backwards Compatibility

✅ **Fully Backwards Compatible**

- Old way (by ID) still works: `delete_task(task_id=123)`
- New way (by name) also works: `delete_task(task_name="meeting")`
- Can provide either parameter (but not both)
- No breaking changes to existing code

## Files Changed

| File | Lines Changed | Purpose |
|------|--------------|---------|
| `delete_task.py` | +50 | Added task_name search logic |
| `complete_task.py` | +50 | Added task_name search logic |
| `update_task.py` | +50 | Added task_name search logic |
| `chat_agent.py` | ~30 | Updated tool definitions and instructions |
| **Total** | **~180** | **Complete feature implementation** |

## Deployment

The backend server has been restarted with all changes:
```
✅ Backend running at: http://127.0.0.1:8001
✅ All changes loaded
✅ Ready for testing
```

## Next Steps

1. **Test** the feature with your chatbot
2. **Try** deleting tasks by name
3. **Report** any issues or edge cases
4. **Enjoy** the more natural conversation flow!

## Example Conversation

```
User: Show me my tasks
Bot: Here are your tasks:
     1. Meeting at 2pm
     2. Buy groceries
     3. Call dentist

User: Delete the meeting task
Bot: I've deleted the 'Meeting at 2pm' task.

User: Mark groceries as done
Bot: Great! I've marked 'Buy groceries' as complete.

User: Update dentist to call mom
Bot: I've updated the task from 'Call dentist' to 'Call mom'.
```

No more asking for IDs! Just natural conversation! 🎉
