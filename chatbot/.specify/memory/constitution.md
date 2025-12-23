<!--
Sync Impact Report:
Version: 1.0.0 (Initial constitution creation)
Modified Principles: N/A (new document)
Added Sections: All sections are new
Removed Sections: N/A
Templates Status:
  ✅ .specify/templates/plan-template.md - reviewed, aligns with constitution
  ✅ .specify/templates/spec-template.md - reviewed, aligns with constitution
  ✅ .specify/templates/tasks-template.md - reviewed, aligns with constitution
  ✅ .claude/commands/*.md - reviewed, no outdated references found
Follow-up TODOs:
  - Review Better Auth integration details once authentication mechanism is finalized
  - Establish specific SLOs for performance metrics once baseline established
-->

# AI-Powered Todo Chatbot Constitution

## Core Principles

### I. Agentic Development Workflow

Development MUST follow the strict sequence: Write Specification → Generate Plan → Break into Tasks → Implement via Claude Code. No manual coding is permitted during implementation phases to ensure systematic, verifiable development with full traceability.

**Rationale**: Enforces disciplined, AI-assisted development with clear separation between design and execution, reducing ad-hoc changes and ensuring all implementation decisions are documented and reviewable.

### II. Stateless Architecture

The backend server MUST be stateless. All conversation state and application data MUST be persisted to the database. No session data or application state may be held in server memory across requests.

**Requirements**:
- FastAPI endpoints are request-scoped only
- Conversation history stored in database
- MCP server operations are atomic and idempotent
- Horizontal scaling MUST be possible without coordination
- Server restarts MUST NOT lose any user state

**Rationale**: Ensures high scalability, resilience, and enables horizontal scaling. Supports cloud-native deployment patterns and simplifies recovery from failures.

### III. Natural Language Interaction First

User experience MUST prioritize natural, conversational language. Users should interact with their todo lists using everyday language without needing to learn specific command syntax or structure.

**Requirements**:
- AI agent interprets intent from natural language
- Support for ambiguous and conversational phrasing
- Graceful handling of unclear requests with clarifying questions
- Friendly, confirmatory responses after actions
- Context awareness across conversation turns

**Rationale**: Reduces cognitive load on users and creates an intuitive experience that feels like talking to an assistant rather than operating a traditional CRUD interface.

### IV. Modularity Through MCP Tools

Task operations MUST be exposed as clearly defined, stateless MCP tools. The AI agent interacts with tasks exclusively through these tools, promoting modularity and extensibility.

**Required MCP Tools**:
- `add_task`: Create task with title, optional description, due date, priority
- `list_tasks`: Retrieve tasks with filtering (status, priority) and sorting (created_at, due_date, priority)
- `complete_task`: Mark task complete by ID
- `delete_task`: Permanently remove task by ID
- `update_task`: Modify task attributes by ID

**Tool Contract Requirements**:
- Each tool MUST be idempotent where applicable
- Tools MUST validate all inputs and return clear errors
- Tools MUST operate atomically (all-or-nothing)
- Tool responses MUST include success confirmation or detailed error messages

**Rationale**: Separation of concerns allows independent evolution of AI reasoning and task management logic. MCP standardization enables future extensibility (e.g., adding new task types or integrations).

### V. Data-Driven Context & Persistence

ALL conversation history and task data MUST be stored in the database. The system MUST support seamless conversation resumption across sessions without context loss.

**Requirements**:
- Every user message stored before AI processing
- Every assistant response persisted after generation
- Task operations logged with timestamps and user context
- Conversation sessions tracked with unique IDs
- No ephemeral state relied upon for user experience

**Rationale**: Enables audit trails, debugging, conversation analytics, and consistent multi-session experiences. Data persistence is foundational for stateless architecture.

### VI. Robustness & Error Handling

The system MUST handle errors gracefully and provide clear, actionable feedback to users. All operations MUST confirm success or explain failures in plain language.

**Requirements**:
- Database errors handled with user-friendly messages
- Missing or invalid task IDs explained clearly
- AI agent failures trigger fallback responses
- Timeout handling for long operations
- Validation errors expressed conversationally (e.g., "I couldn't find that task" vs. "404 Not Found")

**Rationale**: User trust depends on predictable, transparent behavior. Graceful error handling prevents frustration and maintains conversational flow.

### VII. Test-First Quality (NON-NEGOTIABLE)

All features MUST be developed test-first following the Red-Green-Refactor cycle:
1. Write tests that capture requirements
2. Verify tests FAIL (Red)
3. Implement minimal code to pass tests (Green)
4. Refactor for quality (Refactor)

**Test Categories Required**:
- **Unit tests**: Individual functions and MCP tools
- **Integration tests**: FastAPI endpoints, database operations, AI agent tool invocation
- **Contract tests**: MCP tool interfaces and responses
- **End-to-end tests**: Full conversational flows from user input to task operations

**Rationale**: Test-first development ensures requirements are testable, reduces defects, and provides regression safety. Non-negotiable to maintain quality at scale.

### VIII. Simplicity & YAGNI

Design MUST prioritize simplicity. Implement only what is specified. Do not add features, abstractions, or complexity for hypothetical future needs.

**Constraints**:
- No premature abstractions or design patterns unless justified
- No additional features beyond specification
- No over-engineering for scale not yet needed
- Complexity MUST be justified in ADRs

**Rationale**: Reduces maintenance burden, accelerates delivery, and keeps codebase understandable. Future needs can be addressed when they become real requirements.

## Technology Stack

**Mandatory Technologies**:
- **Frontend**: OpenAI ChatKit - conversational UI
- **Backend**: Python FastAPI - API gateway and orchestration
- **AI Framework**: OpenAI Agents SDK - intent recognition and tool orchestration
- **MCP Server**: Official MCP SDK - task operation exposure
- **ORM**: SQLModel - type-safe database interactions
- **Database**: Neon Serverless PostgreSQL - persistent data store
- **Authentication**: Better Auth (integration details TBD)

**Stack Rationale**:
- Modern Python async stack for performance
- Type safety through Pydantic/SQLModel
- Serverless database aligns with stateless architecture
- MCP provides standardized AI-tool interaction

## Architecture Overview

The system follows a service-oriented, event-driven architecture with clear separation of concerns:

```
┌─────────────────┐
│  ChatKit UI     │  User natural language input
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │  API gateway, conversation manager
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OpenAI Agents   │  Intent recognition, tool selection
│      SDK        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MCP Server     │  Stateless task operations
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Neon DB        │  Persistent storage
│  (PostgreSQL)   │
└─────────────────┘
```

**Component Responsibilities**:

1. **ChatKit UI (Frontend)**: User-facing conversational interface, message display, input handling
2. **FastAPI Server (Backend)**: Request routing, conversation persistence, AI agent orchestration, authentication
3. **OpenAI Agents SDK**: Natural language understanding, intent extraction, MCP tool invocation, response generation
4. **MCP Server**: Task CRUD operations, input validation, database interactions via SQLModel
5. **Neon DB**: Data persistence for tasks, conversations, messages

**Data Flow**:
1. User sends message via ChatKit
2. FastAPI receives message, stores in database
3. FastAPI retrieves conversation history from database
4. FastAPI invokes OpenAI Agent with message + history
5. Agent determines intent and calls appropriate MCP tool(s)
6. MCP server executes task operation, returns result
7. Agent generates natural language response
8. FastAPI stores assistant response in database
9. FastAPI returns response to ChatKit for display

## Data Model

The database schema consists of three core entities with clear relationships:

### Task Entity

Represents a single todo item.

**Attributes**:
- `user_id` (UUID, NOT NULL, indexed): Owner of the task
- `id` (UUID, PRIMARY KEY): Unique task identifier
- `title` (VARCHAR(500), NOT NULL): Task title
- `description` (TEXT, NULLABLE): Optional detailed description
- `completed` (BOOLEAN, DEFAULT FALSE): Completion status
- `created_at` (TIMESTAMP, NOT NULL): Creation timestamp
- `updated_at` (TIMESTAMP, NOT NULL): Last modification timestamp
- `due_date` (TIMESTAMP, NULLABLE): Optional due date
- `priority` (ENUM: 'low', 'medium', 'high', DEFAULT 'medium'): Task priority

**Indexes**:
- `user_id, completed` (for filtering by status)
- `user_id, priority` (for filtering/sorting by priority)
- `user_id, due_date` (for sorting by due date)

### Conversation Entity

Represents a chat session between user and assistant.

**Attributes**:
- `user_id` (UUID, NOT NULL, indexed): Owner of the conversation
- `id` (UUID, PRIMARY KEY): Unique conversation identifier
- `created_at` (TIMESTAMP, NOT NULL): Session start timestamp
- `updated_at` (TIMESTAMP, NOT NULL): Last message timestamp

**Indexes**:
- `user_id, updated_at` (for retrieving recent conversations)

### Message Entity

Stores individual messages within a conversation.

**Attributes**:
- `user_id` (UUID, NOT NULL, indexed): Owner (for data isolation)
- `id` (UUID, PRIMARY KEY): Unique message identifier
- `conversation_id` (UUID, FOREIGN KEY → Conversation.id, NOT NULL): Parent conversation
- `role` (ENUM: 'user', 'assistant', NOT NULL): Message author
- `content` (TEXT, NOT NULL): Message text
- `created_at` (TIMESTAMP, NOT NULL): Message timestamp

**Indexes**:
- `conversation_id, created_at` (for retrieving messages in order)
- `user_id, conversation_id` (for isolation queries)

**Relationships**:
- Conversation HAS MANY Messages (1:N)
- User HAS MANY Conversations (1:N)
- User HAS MANY Tasks (1:N)

## AI Agent Behavior Philosophy

The OpenAI Agent acts as an intelligent intermediary that translates natural language into structured task operations while maintaining conversational context.

**Core Capabilities**:

1. **Intent Recognition**: Parse user input to identify action intent (add, list, complete, update, delete, query) and extract entities (task titles, IDs, dates, priorities).

2. **Tool Selection & Invocation**: Map recognized intent to appropriate MCP tool(s). Support tool chaining for complex requests (e.g., "show my tasks then delete the first one").

3. **Parameter Extraction**: Extract tool parameters from natural language:
   - Task titles from phrases ("add buy milk" → title: "buy milk")
   - Task IDs from references ("complete the third one" → requires list context)
   - Dates from natural language ("due tomorrow", "next Monday")
   - Priorities from keywords ("high priority", "urgent")
   - Filters from requests ("show completed tasks", "only high priority")

4. **Context Awareness**: Use conversation history to:
   - Resolve ambiguous references ("the first one" → ID from recent list)
   - Maintain topic continuity across turns
   - Handle follow-up questions without re-stating context

5. **Confirmation & Error Handling**:
   - Confirm successful operations: "I've added 'buy milk' to your tasks."
   - Handle "not found" gracefully: "I couldn't find that task. Would you like to see your current tasks?"
   - Clarify ambiguity: "I found 3 tasks. Which one did you mean? 1) ..., 2) ..., 3) ..."
   - Recover from tool errors: Explain failure, suggest alternative

6. **Natural Response Generation**: Responses should feel conversational, not robotic. Use varied phrasing, acknowledge user intent, and provide helpful next steps.

**Example Conversations**:

```
User: "Add buy groceries for tomorrow"
Agent: [Calls add_task(title="buy groceries", due_date="2025-12-22")]
Agent: "I've added 'buy groceries' to your tasks with a due date of tomorrow (December 22)."

User: "What do I need to do?"
Agent: [Calls list_tasks()]
Agent: "You have 3 tasks:
1. Buy groceries (due tomorrow, medium priority)
2. Finish report (due Dec 25, high priority)
3. Call dentist (no due date, low priority)"

User: "Mark the first one done"
Agent: [Uses conversation context to resolve ID, calls complete_task(id=<groceries_id>)]
Agent: "Great! I've marked 'Buy groceries' as complete."
```

## Development Workflow

The project MUST follow the Agentic Dev Stack methodology:

**Phase 1: Specification** (`/sp.specify`)
- Capture user requirements in `specs/<feature>/spec.md`
- Define user scenarios, acceptance criteria, functional requirements
- No implementation details - focus on WHAT, not HOW
- Output: Approved specification document

**Phase 2: Planning** (`/sp.plan`)
- Research existing codebase and dependencies
- Design technical architecture in `specs/<feature>/plan.md`
- Create data models, API contracts, architecture decisions
- Identify significant decisions for ADRs
- Output: Technical design documents ready for task breakdown

**Phase 3: Task Breakdown** (`/sp.tasks`)
- Generate dependency-ordered tasks in `specs/<feature>/tasks.md`
- Each task references specific files and acceptance criteria
- Tasks grouped by user story for independent delivery
- Include test tasks (write tests first)
- Output: Executable task list

**Phase 4: Implementation** (`/sp.implement`)
- Execute tasks in order via Claude Code
- Tests written and verified to fail before implementation
- Commit after each task or logical group
- No manual coding - all changes via AI agent
- Output: Working, tested feature

**Phase 5: Review & Documentation** (`/sp.adr`, `/sp.phr`)
- Document architectural decisions in ADRs
- Record prompt-response history in PHRs
- Ensure all significant choices are traceable
- Output: Complete documentation trail

**Quality Gates**:
- Specification MUST be approved before planning
- Plan MUST pass constitution checks before task breakdown
- Tasks MUST include tests before implementation begins
- Tests MUST fail before implementation proceeds
- All tests MUST pass before feature considered complete

## Governance

This constitution supersedes all other development practices and serves as the authoritative source of project principles and standards.

**Amendment Process**:
1. Proposed changes documented with rationale
2. Impact analysis on existing features and workflows
3. Team review and approval required
4. Version number incremented according to semantic versioning
5. Migration plan created for backward-incompatible changes
6. All dependent templates and documentation updated

**Versioning**:
- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principles or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, non-semantic fixes

**Compliance Review**:
- All pull requests MUST verify alignment with constitution principles
- Violations of core principles (Stateless Architecture, Test-First) MUST be rejected
- Complexity additions MUST be justified via ADRs
- Code reviews MUST reference specific constitutional principles where applicable

**Runtime Development Guidance**:
- See `CLAUDE.md` for agent-specific development instructions
- Constitution defines WHAT must be followed; CLAUDE.md defines HOW agents operate

**Ratification & Amendments**:
- Original constitution ratified: 2025-12-21
- Last amended: 2025-12-21
- Current version: 1.0.0

---

**Version**: 1.0.0 | **Ratified**: 2025-12-21 | **Last Amended**: 2025-12-21
