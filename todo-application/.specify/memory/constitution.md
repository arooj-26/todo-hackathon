<!--
Sync Impact Report:
- Version Change: Initial → 1.0.0
- Added Principles:
  * I. Spec-Driven Development
  * II. No Manual Coding
  * III. Monorepo Architecture
  * IV. Clear Separation of Concerns
  * V. Multi-User Multi-Tenancy
  * VI. API-First Design
  * VII. Authentication and Authorization
- Added Sections: Technology Stack, Development Workflow
- Templates Status:
  ✅ plan-template.md (Constitution Check compatible)
  ✅ spec-template.md (Aligned with requirements approach)
  ✅ tasks-template.md (Aligned with parallel/sequential execution)
- Follow-up TODOs: None
-->

# Todo Application Constitution

## Core Principles

### I. Spec-Driven Development

All development MUST follow the Agentic Dev Stack workflow:

- Write specification → Generate plan → Break into tasks → Implement via Claude Code
- No implementation work begins until specifications are written and approved
- All features MUST be documented in `/specs` directory before coding
- Specifications define WHAT and WHY; plans define HOW
- Each feature follows the complete cycle: spec → plan → tasks → implementation

**Rationale**: Ensures clarity of requirements, prevents scope creep, enables better planning and estimation, and creates living documentation that evolves with the codebase.

### II. No Manual Coding

The entire project MUST be implemented by Claude Code:

- No developer should manually write production code
- All code generation happens through Claude Code following specifications
- Manual intervention limited to: writing specs, reviewing code, testing functionality
- Claude Code reads specs and CLAUDE.md files to understand context and implement features

**Rationale**: Maintains consistency, enforces spec-driven workflow, ensures documentation drives implementation, and validates that specifications are complete and unambiguous.

### III. Monorepo Architecture

The project MUST be organized as a monorepo:

- Frontend and backend code in the same repository
- Shared specifications and documentation at root level
- Single source of truth for all project artifacts
- Enables Claude Code to edit both frontend and backend in a single context
- Simplifies dependency management and versioning

**Rationale**: Simplifies coordination between frontend and backend, enables atomic changes across full stack, reduces context switching for both developers and AI agents, and maintains consistency across layers.

### IV. Clear Separation of Concerns

Frontend and backend MUST maintain clear boundaries:

- Frontend code in `/frontend` directory (Next.js 16+ App Router)
- Backend code in `/backend` directory (Python FastAPI)
- Communication only through well-defined REST API contracts
- Each layer has its own CLAUDE.md with layer-specific guidance
- No business logic in frontend; no presentation logic in backend

**Rationale**: Enables independent development and testing, allows technology substitution, prevents tight coupling, and maintains clear ownership of responsibilities.

### V. Multi-User Multi-Tenancy

The application MUST support multiple users with data isolation:

- Each user can only access their own tasks
- User ID required in all API endpoints: `/api/{user_id}/tasks`
- Database queries MUST filter by user_id
- No global or shared tasks across users
- User context established through authentication tokens

**Rationale**: Enables scalable multi-user application, ensures data privacy and security, prevents unauthorized access, and supports future organizational features.

### VI. API-First Design

All functionality MUST be exposed through REST API:

- Backend implements RESTful endpoints following standard HTTP methods
- Frontend communicates exclusively through API (no direct database access)
- API contracts documented before implementation
- Versioned endpoints to support evolution
- Standard status codes and error handling

**Standard Endpoints**:
- GET `/api/{user_id}/tasks` - List all tasks
- POST `/api/{user_id}/tasks` - Create a new task
- GET `/api/{user_id}/tasks/{id}` - Get task details
- PUT `/api/{user_id}/tasks/{id}` - Update a task
- DELETE `/api/{user_id}/tasks/{id}` - Delete a task
- PATCH `/api/{user_id}/tasks/{id}/complete` - Toggle completion

**Rationale**: Decouples frontend and backend, enables multiple clients (web, mobile, CLI), facilitates testing through API contracts, and supports future integrations.

### VII. Authentication and Authorization

Security MUST be enforced at every layer:

- User authentication via Better Auth (signup/signin)
- JWT tokens for session management
- All API endpoints require valid JWT token
- 401 Unauthorized for missing/invalid tokens
- Authorization checks enforce user_id matching
- No endpoint should expose other users' data

**Rationale**: Protects user data, prevents unauthorized access, enables secure multi-user operations, and maintains audit trail through user identification.

## Technology Stack

The following technologies are mandated for consistency and alignment:

| Layer          | Technology                   | Version/Notes              |
|:---------------|:-----------------------------|:---------------------------|
| Frontend       | Next.js (App Router)         | 16+                        |
| Backend        | Python FastAPI               | Latest stable              |
| ORM            | SQLModel                     | Latest stable              |
| Database       | Neon Serverless PostgreSQL   | Managed instance           |
| Authentication | Better Auth                  | Latest stable              |
| Spec-Driven    | Claude Code + Spec-Kit Plus  | As configured              |

**Technology Justification**:
- Next.js: Modern React framework with App Router for optimal performance
- FastAPI: High-performance Python framework with automatic API documentation
- SQLModel: Combines SQLAlchemy and Pydantic for type-safe database operations
- Neon PostgreSQL: Serverless scaling, excellent developer experience
- Better Auth: Modern authentication library with JWT support

**Technology changes require**:
- Constitution amendment (MAJOR version bump)
- Migration plan for existing code
- Updated CLAUDE.md files
- Validation that new technology supports all principles

## Project Structure

The monorepo MUST follow this structure:

```
todo-application/
├── .specify/
│   ├── memory/
│   │   └── constitution.md         # This file
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── adr-template.md
│   │   ├── phr-template.prompt.md
│   │   └── checklist-template.md
│   └── scripts/
│       └── powershell/              # Spec-Kit automation scripts
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/
│   │   ├── task-crud.md
│   │   ├── authentication.md
│   │   └── chatbot.md
│   ├── api/
│   │   ├── rest-endpoints.md
│   │   └── mcp-tools.md
│   ├── database/
│   │   └── schema.md
│   └── ui/
│       ├── components.md
│       └── pages.md
├── history/
│   ├── prompts/                     # Prompt History Records
│   │   ├── constitution/
│   │   ├── general/
│   │   └── <feature-name>/
│   └── adr/                         # Architecture Decision Records
├── CLAUDE.md                        # Root project guidance
├── frontend/
│   ├── CLAUDE.md                    # Frontend-specific guidance
│   └── ... (Next.js app structure)
├── backend/
│   ├── CLAUDE.md                    # Backend-specific guidance
│   └── ... (FastAPI app structure)
├── docker-compose.yml
└── README.md
```

**Structure Requirements**:
- `/specs`: Single source of truth for all requirements
- `/history/prompts`: All AI interactions recorded as PHRs
- `/history/adr`: All architectural decisions documented
- Multiple CLAUDE.md files provide context at appropriate levels
- Clear separation between specs (requirements) and code (implementation)

## Development Workflow

The REQUIRED workflow for all development:

1. **Write/Update Spec**
   - Create or update spec file in `/specs` directory
   - Include user stories, requirements, and success criteria
   - Get spec reviewed and approved before proceeding

2. **Generate Plan** (via `/sp.plan`)
   - Claude Code reads spec and generates implementation plan
   - Plan includes architecture decisions, structure, and approach
   - Review and approve plan before task generation

3. **Generate Tasks** (via `/sp.tasks`)
   - Claude Code breaks plan into actionable tasks
   - Tasks organized by priority and dependencies
   - Each task independently testable and completable

4. **Implement** (via Claude Code)
   - Reference specs using `@specs` notation
   - Claude Code reads relevant specs and CLAUDE.md files
   - Implementation follows specs, plan, and tasks exactly
   - Code generated automatically, no manual coding

5. **Test and Iterate**
   - Test implementation against spec acceptance criteria
   - Iterate on spec if requirements change
   - Update plan and tasks as needed
   - Never modify code without updating spec first

**Workflow Enforcement**:
- No code changes without corresponding spec
- No implementation without approved plan
- No commits without task reference
- All changes tracked through PHRs

## CLAUDE.md Files Strategy

Multiple CLAUDE.md files provide layered context:

### Root CLAUDE.md
- Project overview and objectives
- Spec-Kit Plus structure and commands
- Development workflow and principles
- Links to key documentation
- High-level architecture decisions

### Frontend CLAUDE.md
- Next.js patterns and conventions
- Component structure and organization
- API client implementation patterns
- Styling guidelines and theme system
- Frontend-specific testing approaches

### Backend CLAUDE.md
- FastAPI patterns and conventions
- Project structure and module organization
- API endpoint conventions and standards
- Database access and ORM patterns
- Backend testing and validation
- Running and debugging instructions

**CLAUDE.md Requirements**:
- Each file MUST reference constitution principles
- Layer-specific guidance only (no duplication)
- Concrete examples over abstract rules
- Updated whenever patterns change
- Version controlled with code

## Governance

### Amendment Procedure

Constitution changes require:

1. **Proposal**: Document proposed change with rationale
2. **Impact Analysis**: Assess impact on existing code and specs
3. **Version Bump**: Apply semantic versioning
   - MAJOR: Backward-incompatible changes (principle removal/redefinition)
   - MINOR: New principles or material expansions
   - PATCH: Clarifications, wording improvements, typo fixes
4. **Template Sync**: Update all dependent templates and docs
5. **Migration Plan**: For MAJOR changes, provide migration path
6. **Approval**: Get stakeholder sign-off before committing
7. **Documentation**: Update Sync Impact Report at top of file

### Compliance Reviews

All work MUST comply with constitution:

- PRs must reference relevant principles
- Code reviews verify principle adherence
- Specs must align with core principles
- Plans must include "Constitution Check" section
- Tasks must support principle requirements
- PHRs must be created for all significant work

### Complexity Justification

Any deviation from principles requires:

- Explicit documentation in plan.md "Complexity Tracking" section
- Clear explanation of why simpler alternative insufficient
- Approval from project stakeholders
- ADR documenting the architectural decision
- Migration path to return to principle compliance when possible

### Living Document

This constitution:

- Supersedes all other practices and guidelines
- Evolves with project needs through amendment procedure
- Serves as final arbiter for architectural decisions
- References concrete examples in CLAUDE.md files
- Maintains history through version control and Sync Impact Reports

**Version**: 1.0.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-17
