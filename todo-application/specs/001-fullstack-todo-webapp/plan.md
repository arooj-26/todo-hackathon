# Implementation Plan: Todo Full-Stack Web Application

**Branch**: `001-fullstack-todo-webapp` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fullstack-todo-webapp/spec.md`

## Summary

Transform a console-based todo application into a modern multi-user web application with persistent storage. The system will support user authentication, full CRUD operations on tasks, and enforce strict data isolation between users. The implementation follows a monorepo architecture with Next.js frontend and FastAPI backend communicating through REST API.

**Core Technical Approach**:
- Better Auth for JWT-based authentication
- User-scoped API endpoints with authorization middleware
- SQLModel ORM for type-safe database operations
- Neon Serverless PostgreSQL for persistent storage
- Next.js App Router for modern React patterns

## Technical Context

**Language/Version**:
- Frontend: JavaScript/TypeScript with Next.js 16+
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Next.js 16+, Better Auth, React 19+, TailwindCSS
- Backend: FastAPI, SQLModel, Pydantic v2, python-jose (JWT), passlib (password hashing)

**Storage**: Neon Serverless PostgreSQL with SQLModel ORM

**Testing**:
- Frontend: Jest + React Testing Library
- Backend: pytest + httpx for API testing

**Target Platform**: Web application (browser-based)

**Project Type**: Web application (monorepo with frontend + backend)

**Performance Goals**:
- API response time <200ms for 95th percentile
- Support 100+ concurrent users
- Task operations complete within 2 seconds end-to-end

**Constraints**:
- All API endpoints must enforce user-scoped data access
- JWT tokens must be validated on every protected request
- No direct database access from frontend
- Database queries must filter by user_id

**Scale/Scope**:
- Expected users: 100-1000 initially
- Tasks per user: Up to 1000 tasks
- 5 user stories (P1-P5 priority)
- 33 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development ✅
- Specification completed in spec.md with all user stories and requirements
- This plan defines HOW to implement the WHAT from spec.md
- Tasks will be generated after plan approval
- Implementation follows: spec → plan → tasks → code

### II. No Manual Coding ✅
- All implementation will be performed by Claude Code
- Specifications drive code generation
- Manual work limited to: reviewing specs, testing, approving plans

### III. Monorepo Architecture ✅
- Single repository with `/frontend` and `/backend` directories
- Shared `/specs` directory at root
- Single git repository enables atomic cross-stack changes

### IV. Clear Separation of Concerns ✅
- Frontend (Next.js) in `/frontend` directory - presentation only
- Backend (FastAPI) in `/backend` directory - business logic and data access
- Communication only through REST API contracts
- Separate CLAUDE.md files for frontend and backend guidance

### V. Multi-User Multi-Tenancy ✅
- All API endpoints include `{user_id}` in path
- Database schema includes `user_id` foreign key on tasks table
- Authorization middleware verifies token user_id matches path user_id
- All database queries filtered by authenticated user_id

### VI. API-First Design ✅
- REST API defined before implementation
- Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Frontend uses API client - no direct database access
- Contracts documented in Phase 1

### VII. Authentication and Authorization ✅
- Better Auth provides JWT token generation
- All endpoints require valid JWT in Authorization header
- 401 for missing/invalid tokens
- 403 for unauthorized access to other users' data

**GATE RESULT**: ✅ PASS - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-fullstack-todo-webapp/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (Phase 0-1 output)
├── research.md          # Phase 0 research findings
├── data-model.md        # Phase 1 database schema
├── quickstart.md        # Phase 1 getting started guide
├── contracts/           # Phase 1 API contracts
│   ├── auth-api.yaml    # Authentication endpoints
│   └── tasks-api.yaml   # Task management endpoints
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)
todo-application/
├── .specify/            # Spec-Kit Plus framework
│   ├── memory/
│   │   └── constitution.md
│   ├── templates/
│   └── scripts/
├── specs/               # Feature specifications
├── history/             # PHRs and ADRs
├── CLAUDE.md            # Root-level project guidance
├── frontend/
│   ├── CLAUDE.md        # Frontend-specific guidance
│   ├── app/             # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx     # Task dashboard
│   │   ├── signin/
│   │   ├── signup/
│   │   └── tasks/
│   │       └── [id]/
│   ├── components/      # Reusable React components
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── AuthForms.tsx
│   ├── lib/             # Utilities and API client
│   │   ├── api.ts       # API client with JWT handling
│   │   └── auth.ts      # Better Auth configuration
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── package.json
│   └── tsconfig.json
├── backend/
│   ├── CLAUDE.md        # Backend-specific guidance
│   ├── main.py          # FastAPI application entry
│   ├── models.py        # SQLModel models (User, Task)
│   ├── database.py      # Database connection and session
│   ├── auth/            # Authentication logic
│   │   ├── jwt.py       # JWT token handling
│   │   └── middleware.py # Auth middleware
│   ├── routers/         # API route handlers
│   │   ├── auth.py      # Signup/signin endpoints
│   │   └── tasks.py     # Task CRUD endpoints
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── dependencies.py  # FastAPI dependencies
│   ├── config.py        # Configuration management
│   ├── tests/           # Backend tests
│   │   ├── test_auth.py
│   │   └── test_tasks.py
│   ├── requirements.txt
│   └── pyproject.toml
├── docker-compose.yml   # Local development environment
└── README.md
```

**Structure Decision**: Web application structure selected because the feature requires both a frontend (Next.js) and backend (FastAPI) with clear separation of concerns. The monorepo approach enables Claude Code to edit both layers in a single context while maintaining architectural boundaries through directory structure and CLAUDE.md files.

## Complexity Tracking

No constitutional violations to justify. All complexity is inherent to the requirements:
- Multi-user support requires authentication and authorization (constitutional requirement V, VII)
- Separate frontend/backend aligns with constitution principle IV
- REST API follows constitutional principle VI

