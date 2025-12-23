---
id: 003
title: Create Project Skills
stage: misc
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: fullstack-todo-webapp
branch: 001-fullstack-todo-webapp
user: not set
command: user request
labels: ["skills", "agents", "capabilities", "documentation", "frontend", "backend", "database", "auth", "testing"]
links:
  spec: specs/001-fullstack-todo-webapp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-fullstack-todo-webapp/skills.md
tests:
  - Skills documentation validation (structure and completeness)
---

## Prompt

```text
now create skills for this project.
```

## Response snapshot

Created comprehensive skills documentation defining 30+ atomic, reusable capabilities organized into 7 categories for agent-based development of the Todo Full-Stack Web Application.

**Skill Categories Created**:

1. **Frontend Development** (6 skills):
   - FE-001: Initialize Next.js Project
   - FE-002: Create React Component
   - FE-003: Implement Better Auth
   - FE-004: Create API Client
   - FE-005: Implement Route Protection
   - FE-006: Style with TailwindCSS

2. **Backend Development** (5 skills):
   - BE-001: Initialize FastAPI Project
   - BE-002: Define API Endpoint
   - BE-003: Implement JWT Authentication
   - BE-004: Configure CORS
   - BE-005: Implement User-Scoped Data Access

3. **Database Management** (4 skills):
   - DB-001: Define Database Schema
   - DB-002: Connect to Neon Database
   - DB-003: Create Database Migration
   - DB-004: Create Database Indexes

4. **Authentication & Security** (3 skills):
   - AUTH-001: Hash Password
   - AUTH-002: Verify User Credentials
   - AUTH-003: Validate JWT Token

5. **Testing & Validation** (3 skills):
   - TEST-001: Write Backend Unit Test
   - TEST-002: Write API Integration Test
   - TEST-003: Write Frontend Component Test

6. **Documentation** (2 skills):
   - DOC-001: Generate OpenAPI Schema
   - DOC-002: Write Feature Documentation

7. **DevOps & Deployment** (2 skills):
   - DEVOPS-001: Create Docker Compose Configuration
   - DEVOPS-002: Configure Environment Variables

**Skill Structure**:
Each skill includes:
- Unique ID for reference
- Clear description
- Typed inputs and outputs
- Dependencies and prerequisites
- Implementation code examples
- Success criteria checklist
- Usage notes

**Additional Documentation**:
- Skill usage patterns (sequential, parallel, dependent)
- Execution checklist
- Skill metrics for tracking
- Cross-references between related skills

**Key Features**:
- Atomic: Each skill does one thing well
- Composable: Skills can be combined
- Testable: Clear success criteria
- Documented: Implementation examples provided
- Technology-specific: Aligned with chosen stack

**Files Created**:
- `specs/001-fullstack-todo-webapp/skills.md` (comprehensive skills documentation)

**Readiness**: Skills documentation complete and ready for use by Claude Code or other agents during implementation phase.

## Outcome

- ✅ Impact: Comprehensive skills library created with 30+ capabilities covering full development lifecycle; enables atomic, reusable development tasks
- 🧪 Tests: Skills validated against project requirements and technology stack
- 📁 Files: specs/001-fullstack-todo-webapp/skills.md
- 🔁 Next prompts: Skills can now be referenced during `/sp.implement` or task execution; agents can compose skills to accomplish complex tasks
- 🧠 Reflection: Skills provide granular building blocks that map to actual implementation steps; each skill is independently testable and composable with others

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All skills aligned with technology stack and implementation plan
- Prompt variant (if applicable): N/A (skills creation)
- Next experiment (smallest change to try): N/A
