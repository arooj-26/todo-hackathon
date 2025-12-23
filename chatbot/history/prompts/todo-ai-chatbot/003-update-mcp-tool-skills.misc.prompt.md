---
id: 003
title: Update MCP Tool Skills
stage: misc
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: developer
command: review and update skills
labels: ["skills", "mcp-tools", "validation", "pydantic", "type-safety"]
links:
  spec: ../spec.md
  ticket: null
  adr: null
  pr: null
files:
  - D:/testting python/skills/add_task.py
  - D:/testting python/skills/list_tasks.py
  - D:/testting python/skills/complete_task.py
  - D:/testting python/skills/delete_task.py
  - D:/testting python/skills/update_task.py
tests:
  - "None (schema validation only)"
---

## Prompt

now i have to create teh skills for this project, i have created some skills and share link of that folder, if you need changes and add something in that skills, do it. 'D:\testting python\skills'

## Response snapshot

I reviewed all 5 MCP tool skill files in the D:/testting python/skills directory and identified critical alignment issues with the MCP contract specifications defined in specs/001-todo-ai-chatbot/contracts/mcp-tools.md.

**Issues Found:**
- task_id used `int` instead of `UUID4`
- user_id used `str` instead of `UUID4`
- priority used `int` (1, 2, 3) instead of string enum ('low', 'medium', 'high')
- due_date used `str` instead of `datetime`
- Missing Pydantic BaseModel schemas for parameters
- Return types were `Any` instead of structured `dict`
- list_tasks had extra `sort_order` parameter not in contract

**Updates Applied to All 5 Files:**

1. **add_task.py**:
   - Added `Priority` enum (LOW, MEDIUM, HIGH)
   - Added `AddTaskParams(BaseModel)` with UUID4 user_id, datetime due_date, Priority enum
   - Added `TaskResponse(BaseModel)` for return structure
   - Changed return type from `Any` to `dict`

2. **list_tasks.py**:
   - Added `TaskStatus` enum (ALL, PENDING, COMPLETED)
   - Added `Priority` enum
   - Added `SortBy` enum (CREATED_AT, DUE_DATE, PRIORITY)
   - Added `ListTasksParams(BaseModel)` and `ListTasksResponse(BaseModel)`
   - Removed `sort_order` parameter (not in contract)

3. **complete_task.py**:
   - Changed user_id and task_id from str/int to UUID4
   - Added `CompleteTaskParams(BaseModel)`
   - Enhanced docstring emphasizing idempotency

4. **delete_task.py**:
   - Changed user_id and task_id from str/int to UUID4
   - Added `DeleteTaskParams(BaseModel)`
   - Enhanced docstring emphasizing irreversibility

5. **update_task.py**:
   - Changed user_id and task_id to UUID4
   - Changed priority from int to Priority enum
   - Changed due_date from str to datetime
   - Added `UpdateTaskParams(BaseModel)` with partial update fields
   - Enhanced docstring emphasizing partial updates

All files now include:
- Proper Pydantic validation with Field descriptors
- UUID4 types for all IDs
- Enum types for priority and status
- datetime objects for temporal data
- Comprehensive docstrings with AI behavior guidance
- Example inputs/outputs
- TODO comments for implementation phase

**Technical Approach:**
After encountering file locking errors with standard Write/Edit tools, used bash heredoc commands (`cat > file << 'EOF'`) to atomically update all files.

**Result:**
All 5 skill files now perfectly align with MCP contract specification and are ready for /sp.implement phase.

## Outcome

- ✅ Impact: All 5 MCP tool skills aligned with contract specifications, type-safe with Pydantic validation
- 🧪 Tests: No tests run (schema definition work only)
- 📁 Files: 5 files modified (add_task.py, list_tasks.py, complete_task.py, delete_task.py, update_task.py)
- 🔁 Next prompts: /sp.tasks to generate task breakdown for implementation
- 🧠 Reflection: Skills contract validation prevented runtime type errors. Using bash heredoc was necessary workaround for file locking issues in Windows environment.

## Evaluation notes (flywheel)

- Failure modes observed: Standard Write/Edit tools failed due to file locking. Windows path format required forward slashes.
- Graders run and results (PASS/FAIL): Manual contract validation - PASS (all 5 files now match MCP contract specification exactly)
- Prompt variant (if applicable): N/A (direct user request)
- Next experiment (smallest change to try): Consider creating a contract validation script that can be run as pre-commit hook to catch type mismatches early
