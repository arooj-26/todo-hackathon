# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

## Project Structure

This is a full-stack monorepo application with separate frontend and backend directories.

```
todo-application/
├── .agents/                    # Multi-agent orchestration system
│   ├── lib/                   # Agent and skill base classes
│   ├── skills/                # 30+ atomic skills (7 categories)
│   ├── agents/                # 5 specialized agents
│   ├── orchestrator.py        # Workflow coordination
│   └── README.md              # Agent system documentation
├── .specify/                  # Spec-Driven Development framework
│   ├── memory/
│   │   └── constitution.md    # Project principles (7 core rules)
│   ├── templates/             # Spec, plan, task, PHR, ADR templates
│   └── scripts/               # Automation scripts
├── specs/                     # Feature specifications
│   └── 001-fullstack-todo-webapp/
│       ├── spec.md           # Requirements (5 user stories)
│       ├── plan.md           # Architecture decisions
│       ├── tasks.md          # 106 implementation tasks
│       ├── data-model.md     # Database schema
│       └── contracts/        # API contracts (OpenAPI)
├── history/
│   ├── prompts/              # Prompt History Records (PHRs)
│   │   ├── constitution/     # Constitution-related
│   │   ├── <feature-name>/   # Feature-specific
│   │   └── general/          # General prompts
│   └── adr/                  # Architecture Decision Records
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Settings
│   │   ├── database.py       # DB connection
│   │   ├── dependencies.py   # DI (auth, sessions)
│   │   ├── models/           # SQLModel entities
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   └── auth/             # Authentication logic
│   ├── alembic/              # Database migrations
│   ├── tests/                # pytest tests
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment template
│   ├── Dockerfile            # Backend container
│   └── CLAUDE.md             # Backend development guide
├── frontend/                  # Next.js frontend
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Home page
│   │   ├── auth/             # Auth pages (signin/signup)
│   │   ├── dashboard/        # Dashboard page
│   │   └── api/              # API routes (Better Auth)
│   ├── components/           # React components
│   │   ├── auth/             # Auth components
│   │   ├── tasks/            # Task components
│   │   ├── layout/           # Layout components
│   │   └── ui/               # Reusable UI components
│   ├── lib/                  # Utilities
│   │   ├── api/              # API client (Axios)
│   │   ├── auth/             # Better Auth config
│   │   └── utils/            # Helper functions
│   ├── types/                # TypeScript types
│   ├── hooks/                # Custom React hooks
│   ├── middleware.ts         # Auth middleware
│   ├── package.json          # Node dependencies
│   ├── .env.example          # Environment template
│   ├── Dockerfile            # Frontend container
│   └── CLAUDE.md             # Frontend development guide
├── docker-compose.yml        # Local development environment
├── .gitignore                # Git ignore patterns
├── CLAUDE.md                 # This file (root guide)
└── README.md                 # Project README
```

### Key Directories

**`.agents/`**: Multi-agent orchestration system with 5 specialized agents (Frontend, Backend, Database, SpecWriter, DevOps) and 30+ atomic skills. Used for coordinated autonomous development.

**`.specify/`**: Spec-Driven Development framework with templates for specifications, plans, tasks, PHRs, and ADRs. Enforces constitution-based workflow.

**`specs/`**: Feature specifications with requirements, architecture plans, task breakdowns, data models, and API contracts. Each feature gets its own directory.

**`history/`**: Historical records of prompts (PHRs) and architectural decisions (ADRs). Organized by feature and type for traceability.

**`backend/`**: FastAPI backend with SQLModel ORM, JWT authentication, and Alembic migrations. See backend/CLAUDE.md for detailed patterns.

**`frontend/`**: Next.js frontend with App Router, Better Auth, and TailwindCSS. See frontend/CLAUDE.md for detailed patterns.

### Development Workflow

1. **Specification**: Define requirements in `specs/<feature>/spec.md`
2. **Planning**: Create architecture plan in `specs/<feature>/plan.md`
3. **Tasks**: Break down into testable tasks in `specs/<feature>/tasks.md`
4. **Implementation**: Execute tasks using agents or manual development
5. **Documentation**: Record decisions in ADRs, prompts in PHRs
6. **Testing**: Write tests for each task, validate against acceptance criteria
7. **Review**: Ensure all changes follow constitution principles

### Multi-Agent Orchestration

The `.agents/` system enables coordinated autonomous development:

- **Agents**: Specialized autonomous units (Frontend, Backend, Database, SpecWriter, DevOps)
- **Skills**: Atomic, reusable capabilities (30+ skills across 7 categories)
- **Orchestrator**: Workflow coordinator with dependency resolution and parallel execution
- **Execution**: Agents execute skills to complete tasks, coordinating via message passing

Example workflow:
```
User Request → Orchestrator → Task Assignment → Agent Planning → Skill Execution → Result
```

### Environment Setup

1. **Backend**: Copy `backend/.env.example` to `backend/.env` and configure
2. **Frontend**: Copy `frontend/.env.example` to `frontend/.env.local` and configure
3. **Docker**: Ensure Docker and Docker Compose are installed
4. **Run**: Execute `docker-compose up` to start all services

## Technology Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Authentication**: Better Auth (JWT-based)
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Testing**: Jest + React Testing Library

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Authentication**: python-jose (JWT)
- **Password Hashing**: passlib (bcrypt)
- **Testing**: pytest + httpx

### Database
- **Provider**: Neon Serverless PostgreSQL
- **Migrations**: Alembic

### Development Tools
- **Spec-Driven Development**: Claude Code + Spec-Kit Plus
- **API Documentation**: OpenAPI/Swagger (auto-generated by FastAPI)
- **Version Control**: Git
