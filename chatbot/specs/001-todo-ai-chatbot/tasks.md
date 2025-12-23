# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: ✅ INCLUDED - Following Test-First Quality (Constitution Principle VII - NON-NEGOTIABLE)

**Test Strategy**: Red-Green-Refactor workflow
1. **RED**: Write test first (should FAIL)
2. **GREEN**: Implement code to make test PASS
3. **REFACTOR**: Improve code while keeping tests green

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- Backend: `backend/src/` for source code, `backend/tests/` for tests
- Frontend: `frontend/src/` for source code
- Skills: `skills/` for MCP tool implementations (already created)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure (backend/src/{models,mcp,api,agent,database}, backend/tests/{contract,integration,unit,e2e})
- [ ] T002 Create frontend directory structure (frontend/src/{components,pages,services}, frontend/public, frontend/__tests__)
- [ ] T003 Initialize Python project with requirements.txt (FastAPI 0.104+, OpenAI SDK 1.6+, MCP SDK 0.1+, SQLModel 0.0.14+, Pydantic 2.5+, Uvicorn 0.24+, pytest 7.4+, pytest-asyncio 0.21+, httpx 0.25+, pytest-mock 3.12+)
- [ ] T004 [P] Initialize Next.js frontend with package.json (React, TypeScript, @openai/chatkit, Jest, React Testing Library)
- [ ] T005 [P] Create pytest configuration in backend/pytest.ini (test discovery, asyncio mode, coverage settings)
- [ ] T006 [P] Create test fixtures in backend/tests/conftest.py (database session fixture, test database setup/teardown)
- [ ] T007 [P] Create .env.example files for backend (DATABASE_URL, OPENAI_API_KEY) and frontend (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- [ ] T008 [P] Create backend/README.md with setup instructions from quickstart.md
- [ ] T009 [P] Create frontend/README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models (Test-First)

- [ ] T010 [P] 🔴 Write unit test for Task model in backend/tests/unit/test_task_model.py (test creation, validation, default values, UUID generation)
- [ ] T011 [P] 🔴 Write unit test for Conversation model in backend/tests/unit/test_conversation_model.py (test creation, relationships, timestamps)
- [ ] T012 [P] 🔴 Write unit test for Message model in backend/tests/unit/test_message_model.py (test creation, foreign key relationships, role enum validation)
- [ ] T013 Create database enums (PriorityEnum, RoleEnum) in backend/src/models/__init__.py
- [ ] T014 [P] 🟢 Create Task model with SQLModel in backend/src/models/task.py (id, user_id, title, description, completed, created_at, updated_at, due_date, priority) - tests should now PASS
- [ ] T015 [P] 🟢 Create Conversation model with SQLModel in backend/src/models/conversation.py (id, user_id, created_at, updated_at) - tests should now PASS
- [ ] T016 [P] 🟢 Create Message model with SQLModel in backend/src/models/message.py (id, conversation_id, user_id, role, content, created_at) - tests should now PASS

### Database Infrastructure

- [ ] T017 Setup database connection and engine in backend/src/database/connection.py (SQLModel create_engine with Neon URL, connection pooling)
- [ ] T018 Create database migration script for initial schema in backend/migrations/001_initial_schema.sql (CREATE EXTENSION uuid-ossp, CREATE TYPE enums, CREATE TABLE tasks/conversations/messages with indexes)
- [ ] T019 Create database session dependency in backend/src/database/connection.py (get_session() context manager for FastAPI)
- [ ] T020 🔴 Write integration test for database connection in backend/tests/integration/test_database.py (test connection, test session creation, test transaction rollback)
- [ ] T021 🟢 Verify database connection tests PASS with existing connection.py

### FastAPI Base Infrastructure

- [ ] T022 Create FastAPI application instance in backend/src/api/main.py (app = FastAPI(), CORS middleware for frontend origin)
- [ ] T023 [P] Create Pydantic request/response schemas in backend/src/api/schemas.py (ChatRequest, ChatResponse, ToolCall)
- [ ] T024 Create base error handling middleware in backend/src/api/main.py (exception handlers for validation, database, agent errors)
- [ ] T025 🔴 Write integration test for error handling in backend/tests/integration/test_error_handling.py (test validation errors, test database errors, test graceful degradation)
- [ ] T026 🟢 Verify error handling tests PASS

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Manage Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create, list, complete, delete, and update tasks through natural language conversation

**Independent Test**: Send messages like "add buy groceries", "show my tasks", "mark task 1 as done" and verify tasks are managed correctly through conversation alone

### Contract Tests for MCP Tools (Test-First)

**⚠️ Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T027 [P] 🔴 [US1] Contract test for add_task tool in backend/tests/contract/test_add_task_contract.py (verify params match AddTaskParams schema, verify response matches TaskResponse schema)
- [ ] T028 [P] 🔴 [US1] Contract test for list_tasks tool in backend/tests/contract/test_list_tasks_contract.py (verify params match ListTasksParams schema, verify response has tasks array and count)
- [ ] T029 [P] 🔴 [US1] Contract test for complete_task tool in backend/tests/contract/test_complete_task_contract.py (verify params match CompleteTaskParams schema, verify idempotency)
- [ ] T030 [P] 🔴 [US1] Contract test for delete_task tool in backend/tests/contract/test_delete_task_contract.py (verify params match DeleteTaskParams schema, verify error on non-existent task)
- [ ] T031 [P] 🔴 [US1] Contract test for update_task tool in backend/tests/contract/test_update_task_contract.py (verify params match UpdateTaskParams schema, verify partial update behavior)

### Unit Tests for MCP Tools (Test-First)

- [ ] T032 [P] 🔴 [US1] Unit test for add_task in backend/tests/unit/test_add_task.py (test with mock database, test validation, test error cases, test default priority)
- [ ] T033 [P] 🔴 [US1] Unit test for list_tasks in backend/tests/unit/test_list_tasks.py (test filtering by status/priority, test sorting, test empty results, test user isolation)
- [ ] T034 [P] 🔴 [US1] Unit test for complete_task in backend/tests/unit/test_complete_task.py (test update logic, test user isolation, test task not found)
- [ ] T035 [P] 🔴 [US1] Unit test for delete_task in backend/tests/unit/test_delete_task.py (test deletion, test user isolation, test task not found)
- [ ] T036 [P] 🔴 [US1] Unit test for update_task in backend/tests/unit/test_update_task.py (test partial updates, test validation, test user isolation)

### MCP Tools Implementation (Make Tests Pass)

- [ ] T037 [P] 🟢 [US1] Implement add_task MCP tool in backend/src/mcp/tools/add_task.py (create Task in database, return {task_id, status, title, error}) - contract and unit tests should PASS
- [ ] T038 [P] 🟢 [US1] Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py (query tasks with filters for status/priority/sort_by, return {tasks, count, error}) - tests should PASS
- [ ] T039 [P] 🟢 [US1] Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py (update completed=True, return {task_id, status, title, error}) - tests should PASS
- [ ] T040 [P] 🟢 [US1] Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py (delete task from database, return {task_id, status, title, error}) - tests should PASS
- [ ] T041 [P] 🟢 [US1] Implement update_task MCP tool in backend/src/mcp/tools/update_task.py (partial update of title/description/priority/due_date, return {task_id, status, title, error}) - tests should PASS

### MCP Server Setup

- [ ] T042 [US1] Create MCP server initialization in backend/src/mcp/server.py (import all tools, register with MCP SDK Server)
- [ ] T043 [US1] Create MCP tools __init__.py in backend/src/mcp/tools/__init__.py (export all tool functions)
- [ ] T044 🔴 [US1] Integration test for MCP server in backend/tests/integration/test_mcp_server.py (test tool registration, test tool invocation through server)
- [ ] T045 🟢 [US1] Verify MCP server integration tests PASS

### Agent Integration (Test-First)

- [ ] T046 🔴 [US1] Unit test for agent initialization in backend/tests/unit/test_chat_agent.py (test agent creation, test tool registration, test instructions)
- [ ] T047 🔴 [US1] Integration test for agent runner in backend/tests/integration/test_agent_runner.py (test with mock OpenAI responses, test tool calling, test error handling)
- [ ] T048 🟢 [US1] Create OpenAI Agent initialization in backend/src/agent/chat_agent.py (configure with gpt-4o model, register all 5 MCP tools, set instructions for task management) - tests should PASS
- [ ] T049 🟢 [US1] Implement agent runner in backend/src/agent/chat_agent.py (run_agent function that accepts messages array, executes agent, returns response and tool_calls) - tests should PASS
- [ ] T050 [US1] Add error handling for agent failures in backend/src/agent/chat_agent.py (timeout handling, API errors, invalid tool calls, graceful fallbacks)

### API Endpoint (Test-First)

- [ ] T051 🔴 [US1] Integration test for POST /api/{user_id}/chat in backend/tests/integration/test_chat_endpoint.py (test new conversation, test existing conversation, test message storage, test user isolation)
- [ ] T052 🟢 [US1] Implement POST /api/{user_id}/chat endpoint in backend/src/api/main.py (validate request, get/create conversation, fetch message history, store user message, run agent, store assistant response, return ChatResponse) - tests should PASS
- [ ] T053 [US1] Add conversation management helpers in backend/src/api/main.py (get_or_create_conversation, get_conversation_messages, store_message, update_conversation_timestamp)
- [ ] T054 [US1] Add input validation and error responses in backend/src/api/main.py (empty message check, user_id validation, conversation_id validation)

### Frontend (Test-First)

- [ ] T055 [P] 🔴 [US1] Unit test for API client in frontend/__tests__/api.test.ts (test sendMessage function, test error handling, test request formatting)
- [ ] T056 [P] 🔴 [US1] Component test for ChatInterface in frontend/__tests__/ChatInterface.test.tsx (test message rendering, test input handling, test conversation_id persistence)
- [ ] T057 🟢 [P] [US1] Create API client service in frontend/src/services/api.ts (sendMessage function that POSTs to /api/{user_id}/chat, handles responses and errors) - tests should PASS
- [ ] T058 🟢 [US1] Create ChatInterface component in frontend/src/components/ChatInterface.tsx (integrate OpenAI ChatKit, connect to API client, handle conversation_id persistence in localStorage) - tests should PASS
- [ ] T059 [US1] Create main chat page in frontend/src/pages/index.tsx (render ChatInterface, handle user_id from URL or placeholder)
- [ ] T060 [US1] Add error handling UI in frontend/src/components/ChatInterface.tsx (display network errors, API errors, loading states)

### End-to-End Tests for User Story 1

- [ ] T061 🔴 [US1] E2E test for task creation flow in backend/tests/e2e/test_task_creation_e2e.py (send "add buy groceries", verify task in database, verify conversational response)
- [ ] T062 🔴 [US1] E2E test for task listing flow in backend/tests/e2e/test_task_listing_e2e.py (create tasks, send "show my tasks", verify task list in response)
- [ ] T063 🔴 [US1] E2E test for task completion flow in backend/tests/e2e/test_task_completion_e2e.py (create task, send "mark task done", verify completed=true in database)
- [ ] T064 🔴 [US1] E2E test for task deletion flow in backend/tests/e2e/test_task_deletion_e2e.py (create task, send "delete task", verify task removed from database)
- [ ] T065 🔴 [US1] E2E test for task update flow in backend/tests/e2e/test_task_update_e2e.py (create task, send "change title", verify updated title in database)
- [ ] T066 🟢 [US1] Run all E2E tests and verify PASS (full conversational task management works end-to-end)

**Checkpoint**: At this point, User Story 1 should be fully functional with comprehensive test coverage - users can manage tasks through natural language conversation

---

## Phase 4: User Story 2 - Resume Conversations Across Sessions (Priority: P2)

**Goal**: Users can close their session and return later to find conversation history preserved

**Independent Test**: Create a conversation with task operations, simulate browser close (clear session, restart server), then start a new request with the same conversation_id and verify all previous messages and context are restored

### Tests for User Story 2 (Test-First)

- [ ] T067 🔴 [US2] Integration test for conversation persistence in backend/tests/integration/test_conversation_persistence.py (create conversation, fetch history, verify order, test message limit)
- [ ] T068 🔴 [US2] E2E test for conversation resumption in backend/tests/e2e/test_conversation_resume_e2e.py (create conversation, store conversation_id, simulate restart, resume with same ID, verify context preserved)
- [ ] T069 🔴 [US2] Integration test for GET /api/{user_id}/conversations in backend/tests/integration/test_conversation_list.py (test conversation listing, test ordering by updated_at, test user isolation)

### Implementation for User Story 2

- [ ] T070 🟢 [US2] Add conversation history retrieval optimization in backend/src/api/main.py (limit message history to last 50 messages for performance, ordered by created_at ASC) - persistence test should PASS
- [ ] T071 🟢 [US2] Implement conversation_id persistence in frontend/src/components/ChatInterface.tsx (save to localStorage on each response, retrieve on mount, allow starting new conversation)
- [ ] T072 [US2] Add conversation resume UI in frontend/src/components/ChatInterface.tsx (show "Resume conversation" or "Start new" options when returning user detected)
- [ ] T073 🟢 [US2] Add conversation list endpoint GET /api/{user_id}/conversations in backend/src/api/main.py (query recent conversations ordered by updated_at DESC, limit 10) - list test should PASS
- [ ] T074 [US2] Create conversation history component in frontend/src/components/ConversationHistory.tsx (display recent conversations, allow selecting to resume)
- [ ] T075 [US2] Integrate conversation history into main page in frontend/src/pages/index.tsx (show sidebar with recent conversations, handle selection)
- [ ] T076 🟢 [US2] Run conversation resumption E2E test and verify PASS

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can manage tasks and resume conversations seamlessly

---

## Phase 5: User Story 3 - Filter and Search Tasks (Priority: P3)

**Goal**: Users can ask the chatbot to show specific subsets of their tasks (pending, completed, all)

**Independent Test**: Create multiple tasks (some completed, some pending), then ask "show only pending tasks" or "what have I finished?" and verify the correct subset is returned

### Tests for User Story 3 (Test-First)

- [ ] T077 🔴 [US3] E2E test for task filtering in backend/tests/e2e/test_task_filtering_e2e.py (create mixed tasks, test "show pending", test "show completed", test "show all", verify correct subsets)
- [ ] T078 🔴 [US3] E2E test for priority filtering in backend/tests/e2e/test_priority_filtering_e2e.py (create tasks with different priorities, test "show high priority", verify filtering)
- [ ] T079 🔴 [US3] E2E test for task sorting in backend/tests/e2e/test_task_sorting_e2e.py (create tasks with due dates, test "what's due soon", verify sorted by due_date)

### Implementation for User Story 3

- [ ] T080 🟢 [US3] Enhance agent instructions in backend/src/agent/chat_agent.py (add examples for filtering: "what's pending?" → list_tasks(status='pending'), "what have I completed?" → list_tasks(status='completed')) - filtering test should PASS
- [ ] T081 🟢 [US3] Add priority filtering support to agent in backend/src/agent/chat_agent.py (recognize "high priority tasks", "urgent tasks" → list_tasks(priority='high')) - priority test should PASS
- [ ] T082 🟢 [US3] Add sorting support to agent in backend/src/agent/chat_agent.py (recognize "what's due soon?" → list_tasks(sort_by='due_date'), "show by priority" → list_tasks(sort_by='priority')) - sorting test should PASS
- [ ] T083 [US3] Improve response formatting for filtered lists in backend/src/agent/chat_agent.py (agent returns organized, readable task lists with context like "Here are your 3 pending tasks:")

**Checkpoint**: All core user stories (US1, US2, US3) are now independently functional with test coverage

---

## Phase 6: User Story 4 - Handle Ambiguous or Complex Requests (Priority: P3)

**Goal**: The AI agent gracefully handles unclear, ambiguous, or complex requests, asking clarifying questions when needed

**Independent Test**: Send ambiguous commands like "delete the meeting" (when multiple meetings exist) or complex requests like "add milk and show tasks", verifying the agent asks for clarification or chains operations appropriately

### Tests for User Story 4 (Test-First)

- [ ] T084 🔴 [US4] E2E test for ambiguity handling in backend/tests/e2e/test_ambiguity_handling_e2e.py (create multiple "meeting" tasks, send "delete the meeting", verify agent asks for clarification)
- [ ] T085 🔴 [US4] E2E test for multi-step operations in backend/tests/e2e/test_multi_step_e2e.py (send "add milk and show tasks", verify both operations executed, verify conversational confirmation)
- [ ] T086 🔴 [US4] E2E test for context awareness in backend/tests/e2e/test_context_awareness_e2e.py (list tasks, then send "delete the first one", verify agent uses recent context)

### Implementation for User Story 4

- [ ] T087 🟢 [US4] Enhance agent instructions for ambiguity detection in backend/src/agent/chat_agent.py (add guidance for when to ask clarifying questions, provide examples of ambiguous requests) - ambiguity test should PASS
- [ ] T088 🟢 [US4] Add multi-step operation handling in backend/src/agent/chat_agent.py (enable agent to chain multiple tool calls: list_tasks to find task, then delete_task with confirmed ID) - multi-step test should PASS
- [ ] T089 [US4] Implement clarification patterns in backend/src/agent/chat_agent.py (when delete/update targets multiple matches, agent should list options and ask user to specify)
- [ ] T090 🟢 [US4] Add conversation context awareness in backend/src/agent/chat_agent.py (enable "delete the first one" by referencing recent list_tasks results in conversation history) - context test should PASS
- [ ] T091 [US4] Improve error messages for edge cases in backend/src/agent/chat_agent.py (task not found → offer to show tasks, empty message → guide user with examples)

**Checkpoint**: All user stories (US1, US2, US3, US4) should now be independently functional with intelligent conversation handling and full test coverage

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, deployment readiness, and production quality

### Testing & Quality

- [ ] T092 [P] Add test coverage reporting in backend/pytest.ini (coverage threshold 80%, generate HTML reports)
- [ ] T093 [P] Create test runner script in backend/run_tests.sh (run all test categories with coverage, fail if below threshold)
- [ ] T094 [P] Add performance tests in backend/tests/performance/test_response_time.py (verify <3s response time for simple operations, verify concurrent user handling)

### Production Readiness

- [ ] T095 [P] Add comprehensive logging in backend/src/api/main.py (log all requests, responses, tool calls, errors with timestamps and user_id for debugging)
- [ ] T096 [P] Add database connection health check endpoint GET /health in backend/src/api/main.py (verify database connectivity, return 200 if healthy)
- [ ] T097 [P] 🔴 Write integration test for health check in backend/tests/integration/test_health_check.py (test healthy state, test database down scenario)
- [ ] T098 🟢 [P] Verify health check test PASS
- [ ] T099 [P] Optimize database queries in all MCP tools (ensure composite indexes are used, add query profiling if needed)
- [ ] T100 [P] Add request timeout handling in backend/src/api/main.py (30 second timeout for agent operations, graceful timeout responses)
- [ ] T101 [P] Implement rate limiting for API endpoint in backend/src/api/main.py (prevent abuse, reasonable limits for single user: 60 requests/minute)
- [ ] T102 [P] Add user data isolation verification in backend/src/mcp/tools/__init__.py (ensure all database queries include WHERE user_id filter)

### Documentation & Deployment

- [ ] T103 [P] Create deployment guide in backend/README.md (environment setup, database migration steps, Neon configuration, OpenAI API key setup)
- [ ] T104 [P] Add environment validation on startup in backend/src/api/main.py (check DATABASE_URL, OPENAI_API_KEY are set, fail fast with clear error messages)
- [ ] T105 Create frontend deployment guide in frontend/README.md (Vercel/GitHub Pages deployment, domain allowlist configuration for ChatKit, environment variables)
- [ ] T106 Add loading and error states polish in frontend/src/components/ChatInterface.tsx (smooth transitions, retry buttons, helpful error messages)
- [ ] T107 Run quickstart.md validation (verify setup instructions work end-to-end on clean environment)
- [ ] T108 Create end-to-end test suite runner in backend/run_e2e_tests.sh (run all E2E tests, generate report)
- [ ] T109 Add CI/CD configuration in .github/workflows/test.yml (run tests on PR, require passing tests for merge)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel if staffed (independent implementations)
  - Or sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3) → US4 (P3)
- **Polish (Phase 7)**: Depends on desired user stories being complete (recommend US1 minimum for MVP)

### Test-First Workflow (Critical)

Within each user story, **MUST** follow Red-Green-Refactor:

1. **🔴 RED**: Write tests first (contract tests, unit tests) - tests MUST FAIL initially
2. **🟢 GREEN**: Implement code to make tests PASS
3. **🔵 REFACTOR**: Improve code quality while keeping tests green
4. **✅ VERIFY**: Run integration and E2E tests to verify full functionality

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Builds on US1 architecture but independently testable
- **User Story 3 (P3)**: Can start after Foundational - Uses US1 tools but adds filtering intelligence
- **User Story 4 (P3)**: Can start after Foundational - Enhances US1 with better conversation handling

### Within Each User Story

**Test-First Order** (Non-Negotiable):
1. Contract tests (define interface expectations) - FAIL
2. Unit tests (test logic with mocks) - FAIL
3. Implementation (make tests PASS) - GREEN
4. Integration tests (test with real dependencies) - VERIFY
5. E2E tests (test full user flows) - VERIFY

### Parallel Opportunities

**Setup Phase**:
- T004-T009: All initialization tasks can run in parallel

**Foundational Phase** (models):
- T010-T012: All model unit tests in parallel
- T014-T016: All model implementations in parallel (after tests written)

**User Story 1** (major parallelism):
- T027-T031: All 5 contract tests in parallel
- T032-T036: All 5 unit tests in parallel
- T037-T041: All 5 MCP tool implementations in parallel (after tests written)
- T055-T056: Frontend tests in parallel
- T057-T058: Frontend implementation in parallel

**Polish Phase**:
- T092-T105: Most polish tasks can run in parallel

---

## Test Coverage Summary

### Test Categories

1. **Unit Tests** (24 tests)
   - Database models: 3 tests
   - MCP tools: 5 tests
   - Agent: 1 test
   - API client: 1 test
   - Components: 1 test

2. **Contract Tests** (5 tests)
   - One per MCP tool (verify interface compliance)

3. **Integration Tests** (8 tests)
   - Database connection: 1 test
   - Error handling: 1 test
   - MCP server: 1 test
   - Agent runner: 1 test
   - Chat endpoint: 1 test
   - Conversation persistence: 1 test
   - Conversation list: 1 test
   - Health check: 1 test

4. **End-to-End Tests** (13 tests)
   - Task operations: 5 tests (create, list, complete, delete, update)
   - Conversation resumption: 1 test
   - Task filtering: 3 tests (status, priority, sorting)
   - Ambiguity handling: 3 tests (ambiguity, multi-step, context)
   - Performance: 1 test

**Total Tests**: 50 tests ensuring comprehensive coverage

### Coverage Goals

- **Minimum**: 80% code coverage (enforced by pytest configuration)
- **Target**: 90%+ coverage for business logic (MCP tools, agent, API endpoints)
- **All user stories**: Must have E2E tests verifying full conversational flows

---

## Parallel Example: User Story 1 (Test-First)

```bash
# Step 1: Launch all contract tests together (RED phase):
Task T027: "Contract test for add_task tool" (SHOULD FAIL)
Task T028: "Contract test for list_tasks tool" (SHOULD FAIL)
Task T029: "Contract test for complete_task tool" (SHOULD FAIL)
Task T030: "Contract test for delete_task tool" (SHOULD FAIL)
Task T031: "Contract test for update_task tool" (SHOULD FAIL)

# Step 2: Launch all unit tests together (RED phase):
Task T032: "Unit test for add_task" (SHOULD FAIL)
Task T033: "Unit test for list_tasks" (SHOULD FAIL)
Task T034: "Unit test for complete_task" (SHOULD FAIL)
Task T035: "Unit test for delete_task" (SHOULD FAIL)
Task T036: "Unit test for update_task" (SHOULD FAIL)

# Step 3: Implement all MCP tools in parallel (GREEN phase):
Task T037: "Implement add_task MCP tool" (tests should PASS)
Task T038: "Implement list_tasks MCP tool" (tests should PASS)
Task T039: "Implement complete_task MCP tool" (tests should PASS)
Task T040: "Implement delete_task MCP tool" (tests should PASS)
Task T041: "Implement update_task MCP tool" (tests should PASS)

# Step 4: Run E2E tests (VERIFY phase):
Task T061-T066: "E2E tests for all task operations" (SHOULD ALL PASS)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only with Full Tests)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T026) ⚠️ MUST finish before user stories
3. Complete Phase 3: User Story 1 with tests (T027-T066)
   - Write contract tests (T027-T031) - FAIL
   - Write unit tests (T032-T036) - FAIL
   - Implement MCP tools (T037-T041) - PASS
   - Implement server/agent/API (T042-T054) - PASS
   - Implement frontend (T055-T060) - PASS
   - Run E2E tests (T061-T066) - VERIFY
4. **STOP & VALIDATE**: All tests should be GREEN
5. Optionally add Phase 7 polish (T092-T109)
6. Deploy/demo MVP with confidence (tests prove it works)

### Test-Driven Development Benefits

- **Confidence**: 50 tests ensure all features work correctly
- **Regression Prevention**: Tests catch breaking changes immediately
- **Documentation**: Tests show how code should be used
- **Refactoring Safety**: Can improve code while tests stay green
- **Constitution Compliance**: Follows Principle VII (Test-First Quality - NON-NEGOTIABLE)

### Incremental Delivery with Tests

1. Complete Setup + Foundational (T001-T026) → Foundation tested and ready
2. Add User Story 1 (T027-T066) → Full test coverage → **Deploy/Demo (MVP!)**
3. Add User Story 2 (T067-T076) → Test conversation persistence → Deploy/Demo
4. Add User Story 3 (T077-T083) → Test filtering → Deploy/Demo
5. Add User Story 4 (T084-T091) → Test ambiguity handling → Deploy/Demo
6. Polish (T092-T109) → Production ready with CI/CD
7. Each story adds value without breaking previous stories (proven by tests)

---

## Summary

**Total Tasks**: 109 (including 50 test tasks)
- Setup: 9 tasks
- Foundational: 17 tasks (BLOCKING) - includes model tests
- User Story 1 (P1): 40 tasks (MVP) - includes 15 test tasks
- User Story 2 (P2): 10 tasks - includes 3 test tasks
- User Story 3 (P3): 7 tasks - includes 3 test tasks
- User Story 4 (P3): 8 tasks - includes 3 test tasks
- Polish: 18 tasks - includes 4 test tasks

**Test Breakdown**: 50 test tasks
- Contract tests: 5
- Unit tests: 24
- Integration tests: 8
- End-to-End tests: 13

**Parallel Opportunities**: 35+ tasks marked [P] can run concurrently

**MVP Scope with Tests**: Setup + Foundational + User Story 1 = 66 tasks (includes 15 test tasks)

**Test Coverage**: Minimum 80%, target 90%+ for business logic

**Independent Test Criteria**:
- US1: Natural language task management (5 E2E tests)
- US2: Conversation persistence (1 E2E test)
- US3: Task filtering (3 E2E tests)
- US4: Ambiguous requests (3 E2E tests)

**Key Success Factors**:
- ✅ Test-First Quality (Constitution Principle VII - NON-NEGOTIABLE)
- ✅ Red-Green-Refactor workflow enforced
- ✅ 50 tests ensure comprehensive coverage
- ✅ Each user story independently testable
- ✅ All tests must PASS before deployment

---

## Notes

- 🔴 = RED phase (write test, should FAIL)
- 🟢 = GREEN phase (implement code, test should PASS)
- 🔵 = REFACTOR phase (improve code, tests stay GREEN)
- ✅ = VERIFY phase (run integration/E2E tests)
- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests FAIL before implementing (Red-Green-Refactor)
- Commit after tests pass for each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are exact and ready for implementation
- Skills folder already exists with tool stubs - will be moved/integrated into backend/src/mcp/tools/
- **NEVER implement without tests first** - Constitution Principle VII is non-negotiable
