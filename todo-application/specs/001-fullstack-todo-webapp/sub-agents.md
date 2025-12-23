# Sub-Agents: Todo Full-Stack Web Application

**Feature**: 001-fullstack-todo-webapp
**Date**: 2025-12-17
**Purpose**: Define specialized autonomous agents for collaborative development

## Overview

Sub-agents are specialized autonomous entities with specific responsibilities, capabilities, and decision-making authority. They collaborate to implement features following the spec-driven development workflow, each focusing on their domain of expertise.

### Agent Architecture

```
                    ┌─────────────────────┐
                    │  Orchestrator       │
                    │  (User/Main Agent)  │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
        │ SpecWriter   │ │ Database │ │ DevOps     │
        │ Agent        │ │ Admin    │ │ Agent      │
        └───────┬──────┘ └────┬─────┘ └─────┬──────┘
                │              │              │
                │     ┌────────▼────────┐     │
                │     │                 │     │
        ┌───────▼─────▼──┐      ┌──────▼─────▼──────┐
        │ Frontend       │      │ Backend           │
        │ Developer      │◄────►│ Developer         │
        └────────────────┘      └───────────────────┘
```

### Core Principles

1. **Single Responsibility**: Each agent owns a specific domain
2. **Clear Interfaces**: Defined communication protocols between agents
3. **Autonomous Decision-Making**: Agents make decisions within their domain
4. **Collaborative**: Agents coordinate for cross-cutting concerns
5. **Spec-Driven**: All agents follow specifications and constitution

---

## Agent Definitions

### 1. FrontendDeveloper_Agent

**Agent ID**: `FRONTEND-001`
**Domain**: Next.js frontend, UI components, client-side logic
**Autonomy Level**: High (within frontend domain)

#### Responsibilities

**Primary**:
- Implement Next.js application with App Router
- Create React components following design specifications
- Integrate Better Auth for authentication UI
- Build API client for backend communication
- Implement route protection and navigation
- Apply TailwindCSS styling
- Write frontend tests (Jest + React Testing Library)

**Secondary**:
- Collaborate with Backend agent on API contracts
- Report UI/UX issues to SpecWriter agent
- Coordinate with DevOps on deployment configuration

#### Skills

Can execute these skills autonomously:
- **FE-001**: Initialize Next.js Project
- **FE-002**: Create React Component
- **FE-003**: Implement Better Auth
- **FE-004**: Create API Client
- **FE-005**: Implement Route Protection
- **FE-006**: Style with TailwindCSS
- **TEST-003**: Write Frontend Component Test

Can request from other agents:
- **BE-002**: API endpoint definitions (from Backend agent)
- **DOC-002**: Component documentation (from SpecWriter agent)
- **DEVOPS-002**: Environment configuration (from DevOps agent)

#### Decision-Making Authority

**Can Decide**:
- Component structure and organization
- State management approach (useState, useContext, etc.)
- CSS class application and styling details
- Client-side validation rules
- UI interaction patterns (loading states, error messages)
- Frontend routing structure

**Must Consult**:
- API contract changes → Backend agent
- New route requirements → SpecWriter agent
- Authentication flow changes → Backend agent
- Environment variables → DevOps agent

**Cannot Decide**:
- Backend API design
- Database schema changes
- Authentication token format
- CORS configuration

#### Interfaces

**Inputs**:
- Feature specification from SpecWriter agent
- API contracts (OpenAPI specs) from Backend agent
- Component design specs
- User stories and acceptance criteria

**Outputs**:
- Implemented React components
- Styled UI following design system
- Frontend tests (passing)
- API client with typed functions
- Protected routes configuration

**Communication Protocol**:
```typescript
// Request API endpoint information
interface APIRequest {
  agent: 'frontend'
  request_type: 'api_contract'
  endpoint: string
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
}

// Response from Backend agent
interface APIResponse {
  agent: 'backend'
  endpoint: string
  method: string
  request_schema: object
  response_schema: object
  status_codes: number[]
}
```

#### Success Criteria

**Component Quality**:
- [x] TypeScript types defined for all props
- [x] No TypeScript errors or warnings
- [x] Responsive design (mobile, tablet, desktop)
- [x] Accessible (ARIA labels, keyboard navigation)
- [x] Error handling for all user actions

**Testing**:
- [x] All components have tests
- [x] User interactions covered
- [x] Edge cases tested
- [x] Tests pass in CI/CD

**Integration**:
- [x] API client works with backend
- [x] Authentication flow complete
- [x] Route protection functional
- [x] Error messages user-friendly

#### Example Workflows

**Workflow 1: Implement Task List Component**

1. **Receive**: Task list user story from SpecWriter
2. **Request**: GET /api/{user_id}/tasks contract from Backend agent
3. **Execute**: FE-002 (Create React Component - TaskList)
4. **Execute**: FE-006 (Style with TailwindCSS)
5. **Execute**: TEST-003 (Write Component Test)
6. **Integrate**: Use API client to fetch tasks
7. **Validate**: Test with backend API
8. **Report**: Component complete, tests passing

**Workflow 2: Add Authentication Pages**

1. **Receive**: Authentication user story
2. **Coordinate**: Review auth flow with Backend agent
3. **Execute**: FE-003 (Implement Better Auth)
4. **Execute**: FE-002 (Create signin/signup components)
5. **Execute**: FE-005 (Implement Route Protection)
6. **Execute**: FE-006 (Style auth forms)
7. **Test**: Signin, signup, signout flows
8. **Report**: Authentication complete

---

### 2. BackendDeveloper_Agent

**Agent ID**: `BACKEND-001`
**Domain**: FastAPI backend, API endpoints, business logic
**Autonomy Level**: High (within backend domain)

#### Responsibilities

**Primary**:
- Implement FastAPI application with proper structure
- Create API endpoints following RESTful patterns
- Implement JWT authentication and authorization
- Enforce user-scoped data access
- Configure CORS for frontend communication
- Implement business logic and validation
- Write backend tests (pytest + httpx)

**Secondary**:
- Collaborate with Frontend agent on API contracts
- Coordinate with Database agent on data access patterns
- Report API design issues to SpecWriter agent
- Provide API documentation via OpenAPI

#### Skills

Can execute these skills autonomously:
- **BE-001**: Initialize FastAPI Project
- **BE-002**: Define API Endpoint
- **BE-003**: Implement JWT Authentication
- **BE-004**: Configure CORS
- **BE-005**: Implement User-Scoped Data Access
- **AUTH-001**: Hash Password
- **AUTH-002**: Verify User Credentials
- **AUTH-003**: Validate JWT Token
- **TEST-001**: Write Backend Unit Test
- **TEST-002**: Write API Integration Test
- **DOC-001**: Generate OpenAPI Schema

Can request from other agents:
- **DB-001**: Database models (from Database agent)
- **DB-002**: Database session (from Database agent)
- **DEVOPS-002**: Environment configuration (from DevOps agent)

#### Decision-Making Authority

**Can Decide**:
- API endpoint structure and naming
- Request/response schema design
- HTTP status codes for responses
- Error message formats
- Validation rules (within spec boundaries)
- Business logic implementation details
- API versioning strategy

**Must Consult**:
- Database schema changes → Database agent
- New entity requirements → SpecWriter agent
- Authentication strategy changes → SpecWriter agent
- Performance optimization → Database agent

**Cannot Decide**:
- Database schema structure
- Frontend component design
- Specification changes
- Infrastructure configuration

#### Interfaces

**Inputs**:
- Feature specification from SpecWriter agent
- Database models from Database agent
- API requirements and constraints
- User stories with API needs

**Outputs**:
- Implemented API endpoints
- OpenAPI documentation (auto-generated)
- Backend tests (passing)
- JWT authentication middleware
- Request/response schemas (Pydantic)

**Communication Protocol**:
```python
# Provide API contract to Frontend agent
from typing import TypedDict

class APIContract(TypedDict):
    agent: str  # 'backend'
    endpoint: str
    method: str
    request_schema: dict
    response_schema: dict
    status_codes: list[int]
    requires_auth: bool
    authorization_scope: str  # e.g., 'user_must_own_resource'

# Request database operation from Database agent
class DatabaseRequest(TypedDict):
    agent: str  # 'backend'
    operation: str  # 'query' | 'insert' | 'update' | 'delete'
    model: str  # Model class name
    filters: dict
    data: dict
```

#### Success Criteria

**API Quality**:
- [x] All endpoints follow RESTful conventions
- [x] Proper HTTP status codes returned
- [x] Request validation with Pydantic
- [x] User-scoped data access enforced
- [x] JWT authentication on all protected endpoints

**Testing**:
- [x] Unit tests for business logic
- [x] Integration tests for endpoints
- [x] Authorization tests
- [x] Error handling tested
- [x] All tests pass

**Documentation**:
- [x] OpenAPI schema auto-generated
- [x] All endpoints documented
- [x] Request/response examples provided
- [x] Error responses documented

#### Example Workflows

**Workflow 1: Implement Task CRUD Endpoints**

1. **Receive**: Task management user story from SpecWriter
2. **Request**: Task model definition from Database agent
3. **Execute**: BE-002 (Define API Endpoint - List Tasks)
4. **Execute**: BE-002 (Define API Endpoint - Create Task)
5. **Execute**: BE-002 (Define API Endpoint - Update Task)
6. **Execute**: BE-002 (Define API Endpoint - Delete Task)
7. **Execute**: BE-005 (Implement User-Scoped Access for all endpoints)
8. **Execute**: TEST-002 (Write API Integration Tests)
9. **Execute**: DOC-001 (Generate OpenAPI Schema)
10. **Share**: API contracts with Frontend agent
11. **Report**: Endpoints complete, tests passing

**Workflow 2: Implement Authentication**

1. **Receive**: Authentication user story
2. **Request**: User model from Database agent
3. **Execute**: BE-003 (Implement JWT Authentication)
4. **Execute**: AUTH-001 (Hash Password)
5. **Execute**: AUTH-002 (Verify User Credentials)
6. **Execute**: BE-002 (Define signup endpoint)
7. **Execute**: BE-002 (Define signin endpoint)
8. **Execute**: TEST-001 (Write Unit Tests for auth functions)
9. **Execute**: TEST-002 (Write API Integration Tests)
10. **Coordinate**: Share JWT format with Frontend agent
11. **Report**: Authentication complete

---

### 3. DatabaseAdmin_Agent

**Agent ID**: `DATABASE-001`
**Domain**: Database schema, migrations, data access
**Autonomy Level**: Medium (schema changes require approval)

#### Responsibilities

**Primary**:
- Define database schema using SQLModel
- Create and manage Alembic migrations
- Establish connection to Neon PostgreSQL
- Configure connection pooling
- Create database indexes for performance
- Define entity relationships
- Ensure data integrity constraints

**Secondary**:
- Collaborate with Backend agent on data access patterns
- Provide database models to Backend agent
- Report performance issues to Backend agent
- Coordinate with DevOps on database configuration

#### Skills

Can execute these skills autonomously:
- **DB-001**: Define Database Schema
- **DB-002**: Connect to Neon Database
- **DB-003**: Create Database Migration
- **DB-004**: Create Database Indexes

Must coordinate with SpecWriter for:
- Schema changes affecting entities
- New entity additions
- Relationship modifications

#### Decision-Making Authority

**Can Decide**:
- Index creation and optimization
- Connection pool configuration
- Migration rollback procedures
- Field types and constraints (within spec)
- Cascade delete behavior
- Timestamp fields and defaults

**Must Consult**:
- New entity creation → SpecWriter agent
- Entity field additions → SpecWriter agent
- Relationship changes → SpecWriter agent
- Performance tuning → Backend agent

**Cannot Decide**:
- Entity definitions (must come from spec)
- Business rules and validation
- API endpoint design
- Frontend data display

#### Interfaces

**Inputs**:
- Data model specification from SpecWriter agent
- Entity definitions with attributes
- Relationship requirements
- Performance requirements

**Outputs**:
- SQLModel model definitions
- Alembic migration files
- Database connection configuration
- Index definitions
- Database documentation

**Communication Protocol**:
```python
# Provide model to Backend agent
from typing import TypedDict, List

class ModelDefinition(TypedDict):
    agent: str  # 'database'
    model_name: str
    table_name: str
    fields: List[dict]
    relationships: List[dict]
    indexes: List[str]
    constraints: List[str]

# Report migration status
class MigrationStatus(TypedDict):
    agent: str  # 'database'
    migration_id: str
    status: str  # 'pending' | 'applied' | 'failed'
    tables_affected: List[str]
    rollback_available: bool
```

#### Success Criteria

**Schema Quality**:
- [x] All entities from spec defined
- [x] Foreign keys properly configured
- [x] Indexes on performance-critical columns
- [x] Constraints enforce data integrity
- [x] Timestamps on all tables

**Migrations**:
- [x] Migrations apply cleanly
- [x] Rollback available for all migrations
- [x] No data loss on upgrade
- [x] Migration history tracked

**Performance**:
- [x] Connection pooling configured
- [x] Queries use indexes
- [x] No N+1 query patterns
- [x] Database responds <50ms for indexed queries

#### Example Workflows

**Workflow 1: Create Initial Schema**

1. **Receive**: Data model specification from SpecWriter
2. **Execute**: DB-001 (Define Database Schema - User model)
3. **Execute**: DB-001 (Define Database Schema - Task model)
4. **Execute**: DB-002 (Connect to Neon Database)
5. **Execute**: DB-003 (Create Database Migration)
6. **Apply**: Migration to create tables
7. **Execute**: DB-004 (Create Indexes - user_id, email)
8. **Validate**: Tables created, constraints working
9. **Share**: Model definitions with Backend agent
10. **Report**: Schema complete, migrations applied

**Workflow 2: Add Index for Performance**

1. **Receive**: Performance issue report from Backend agent
2. **Analyze**: Query patterns and missing indexes
3. **Execute**: DB-004 (Create Database Indexes)
4. **Execute**: DB-003 (Create Migration for indexes)
5. **Test**: Verify query performance improved
6. **Report**: Index added, performance improved

---

### 4. SpecWriter_Agent

**Agent ID**: `SPEC-001`
**Domain**: Specifications, documentation, requirements
**Autonomy Level**: Medium (gatekeeper for requirements)

#### Responsibilities

**Primary**:
- Create and maintain feature specifications
- Document API contracts in OpenAPI format
- Write data model specifications
- Maintain quickstart and setup guides
- Create and update implementation plans
- Clarify requirements and acceptance criteria
- Ensure specifications align with constitution

**Secondary**:
- Coordinate feature requirements across agents
- Document architectural decisions (ADRs)
- Create PHRs for important decisions
- Update skills documentation as needed
- Maintain sub-agent definitions

#### Skills

Can execute these skills autonomously:
- **DOC-002**: Write Feature Documentation
- All specification and documentation tasks

Can request from other agents:
- Implementation feedback from all agents
- Technical constraints from Backend/Database agents
- UI/UX feedback from Frontend agent

#### Decision-Making Authority

**Can Decide**:
- Specification structure and format
- Documentation organization
- Requirement priorities (with user input)
- Acceptance criteria details
- Documentation standards

**Must Consult**:
- New feature requirements → User/Orchestrator
- Scope changes → User/Orchestrator
- Technology stack changes → User/Orchestrator
- Constitutional changes → User/Orchestrator

**Cannot Decide**:
- Implementation details (belongs to dev agents)
- Technical architecture (belongs to dev agents)
- Infrastructure setup (belongs to DevOps agent)

#### Interfaces

**Inputs**:
- User requirements and feature requests
- Feedback from development agents
- Implementation findings
- Bug reports and issues

**Outputs**:
- Feature specifications (spec.md)
- API contracts (OpenAPI YAML)
- Data models (data-model.md)
- Implementation plans (plan.md)
- Quickstart guides
- ADRs and PHRs

**Communication Protocol**:
```typescript
// Provide specification to development agents
interface SpecificationPackage {
  agent: 'specwriter'
  feature_name: string
  spec_path: string
  user_stories: UserStory[]
  requirements: Requirement[]
  api_contracts: string[]  // Paths to OpenAPI files
  data_model: string  // Path to data model
  acceptance_criteria: AcceptanceCriterion[]
}

// Request clarification from user
interface ClarificationRequest {
  agent: 'specwriter'
  request_type: 'clarification'
  topic: string
  questions: string[]
  suggested_answers: string[][]
}
```

#### Success Criteria

**Specification Quality**:
- [x] All user stories clearly defined
- [x] Acceptance criteria testable
- [x] Requirements unambiguous
- [x] API contracts complete
- [x] No conflicting requirements

**Documentation**:
- [x] Quickstart guide up-to-date
- [x] All APIs documented
- [x] Examples provided
- [x] Troubleshooting included

**Alignment**:
- [x] Specs follow constitution
- [x] All agents have clear guidance
- [x] Requirements traceable to user needs

#### Example Workflows

**Workflow 1: Create Feature Specification**

1. **Receive**: User feature request
2. **Analyze**: Break down into user stories
3. **Draft**: spec.md with user stories and requirements
4. **Define**: API contracts needed
5. **Define**: Data model requirements
6. **Create**: OpenAPI contracts
7. **Create**: data-model.md
8. **Validate**: Spec quality checklist
9. **Distribute**: Share spec with all agents
10. **Report**: Specification complete and distributed

**Workflow 2: Update API Contract**

1. **Receive**: API change request from Backend agent
2. **Analyze**: Impact on Frontend and other consumers
3. **Coordinate**: Discuss with Frontend and Backend agents
4. **Update**: OpenAPI contract files
5. **Update**: Implementation plan if needed
6. **Notify**: All affected agents of changes
7. **Report**: Contract updated, agents notified

---

### 5. DevOps_Agent

**Agent ID**: `DEVOPS-001`
**Domain**: Environment, deployment, infrastructure
**Autonomy Level**: Medium (infrastructure decisions with oversight)

#### Responsibilities

**Primary**:
- Configure development environment
- Manage environment variables
- Create Docker configurations
- Set up CI/CD pipelines
- Configure logging and monitoring
- Manage secrets and credentials
- Document deployment procedures

**Secondary**:
- Collaborate with all agents on environment needs
- Provide deployment support
- Troubleshoot environment issues
- Optimize build and deploy processes

#### Skills

Can execute these skills autonomously:
- **DEVOPS-001**: Create Docker Compose Configuration
- **DEVOPS-002**: Configure Environment Variables

#### Decision-Making Authority

**Can Decide**:
- Docker configuration details
- Environment variable structure
- Build process optimization
- Logging configuration
- Development tooling

**Must Consult**:
- Production infrastructure → User/Orchestrator
- Secret management strategy → User/Orchestrator
- CI/CD pipeline design → User/Orchestrator
- Cloud provider selection → User/Orchestrator

**Cannot Decide**:
- Application architecture
- Technology stack choices
- Database structure
- API design

#### Interfaces

**Inputs**:
- Environment requirements from all agents
- Secret and credential needs
- Deployment requirements
- Build requirements

**Outputs**:
- docker-compose.yml configuration
- .env template files
- Deployment documentation
- CI/CD pipeline configurations
- Environment setup scripts

**Communication Protocol**:
```yaml
# Provide environment configuration
environment_config:
  agent: devops
  environment: development | staging | production
  variables:
    - name: DATABASE_URL
      required: true
      secret: true
      description: PostgreSQL connection string
    - name: BETTER_AUTH_SECRET
      required: true
      secret: true
      description: JWT signing secret
  services:
    - name: frontend
      port: 3000
      env_file: frontend/.env.local
    - name: backend
      port: 8000
      env_file: backend/.env
```

#### Success Criteria

**Environment Setup**:
- [x] All services start successfully
- [x] Environment variables documented
- [x] Secrets properly secured
- [x] Docker containers functional

**Documentation**:
- [x] Setup instructions clear
- [x] Troubleshooting guide complete
- [x] Environment variables documented
- [x] Deployment process documented

#### Example Workflows

**Workflow 1: Set Up Development Environment**

1. **Receive**: Environment requirements from all agents
2. **Execute**: DEVOPS-001 (Create Docker Compose)
3. **Execute**: DEVOPS-002 (Configure Environment Variables)
4. **Create**: .env.example files
5. **Document**: Setup instructions in quickstart.md
6. **Test**: Start all services with docker-compose
7. **Report**: Environment ready, documentation complete

---

## Agent Collaboration Patterns

### Pattern 1: Feature Implementation

**Sequence**: User Story → Full Implementation

```
1. SpecWriter receives user requirement
2. SpecWriter creates specification
   ├─► Defines user stories
   ├─► Creates API contracts
   └─► Defines data model

3. DatabaseAdmin implements schema
   ├─► Creates SQLModel models
   ├─► Generates migration
   └─► Shares models with Backend

4. Backend & Frontend develop in parallel
   ├─► Backend implements API endpoints
   │   └─► Uses models from Database
   ├─► Frontend implements UI components
   │   └─► Uses API contracts from Backend
   └─► Both write tests

5. DevOps ensures environment works
   └─► All agents test in dev environment

6. SpecWriter validates against spec
   └─► All acceptance criteria met
```

### Pattern 2: API Contract First

**Sequence**: Define Contract → Implement Both Sides

```
1. SpecWriter defines API contract (OpenAPI)
2. Backend receives contract
   ├─► Implements endpoint
   ├─► Validates request/response
   └─► Signals "API ready"
3. Frontend receives contract
   ├─► Implements API client
   ├─► Creates UI components
   └─► Integrates with API
4. Integration testing
   └─► Frontend + Backend validate together
```

### Pattern 3: Schema Evolution

**Sequence**: New Entity Need → Schema Update

```
1. SpecWriter identifies new entity need
2. SpecWriter updates data model spec
3. DatabaseAdmin receives update
   ├─► Creates new model
   ├─► Generates migration
   └─► Shares with Backend
4. Backend updates API endpoints
   └─► Adds CRUD for new entity
5. Frontend updates UI
   └─► Adds components for new entity
```

### Pattern 4: Bug Fix

**Sequence**: Issue Discovered → Root Cause → Fix

```
1. Any agent discovers bug
2. Affected agent analyzes
   ├─► Frontend: UI issue
   ├─► Backend: API issue
   ├─► Database: Data issue
   └─► DevOps: Environment issue
3. Agent implements fix
4. Agent writes regression test
5. Agent notifies SpecWriter
6. SpecWriter updates documentation
```

## Agent Communication Protocol

### Message Types

#### 1. Request Message
```json
{
  "from_agent": "frontend",
  "to_agent": "backend",
  "message_type": "request",
  "request_id": "req-001",
  "topic": "api_contract",
  "payload": {
    "endpoint": "/api/{user_id}/tasks",
    "method": "GET"
  },
  "priority": "normal",
  "timestamp": "2025-12-17T10:00:00Z"
}
```

#### 2. Response Message
```json
{
  "from_agent": "backend",
  "to_agent": "frontend",
  "message_type": "response",
  "request_id": "req-001",
  "status": "success",
  "payload": {
    "contract_path": "specs/001-fullstack-todo-webapp/contracts/tasks-api.yaml",
    "endpoint": "/api/{user_id}/tasks",
    "method": "GET",
    "response_schema": {...}
  },
  "timestamp": "2025-12-17T10:05:00Z"
}
```

#### 3. Notification Message
```json
{
  "from_agent": "database",
  "to_agents": ["backend", "specwriter"],
  "message_type": "notification",
  "topic": "schema_updated",
  "payload": {
    "migration_id": "20251217_001",
    "tables_affected": ["tasks"],
    "changes": ["added_column_priority"]
  },
  "timestamp": "2025-12-17T11:00:00Z"
}
```

#### 4. Error Message
```json
{
  "from_agent": "backend",
  "to_agent": "orchestrator",
  "message_type": "error",
  "error_code": "VALIDATION_FAILED",
  "error_message": "Cannot create task: description too long",
  "context": {
    "endpoint": "/api/1/tasks",
    "input": {...}
  },
  "needs_human_intervention": true,
  "timestamp": "2025-12-17T12:00:00Z"
}
```

### Coordination Rules

1. **Async by Default**: Agents work independently, sync only when needed
2. **Explicit Handoffs**: Clear "work complete" signals between agents
3. **Shared Context**: All agents access same specs and plans
4. **Escalation Path**: Blocked agents escalate to orchestrator
5. **State Tracking**: Each agent tracks its work status

## Agent Status and Monitoring

### Status Indicators

Each agent reports status:

```typescript
interface AgentStatus {
  agent_id: string
  agent_name: string
  status: 'idle' | 'working' | 'blocked' | 'waiting' | 'error'
  current_task: string | null
  progress: number  // 0-100
  blocked_by: string | null  // Agent ID if blocked
  last_update: string  // ISO timestamp
}
```

### Example Status Board

```
┌────────────────────────────────────────────────────┐
│ Agent Status Dashboard                             │
├────────────────────┬───────────┬──────────────────┤
│ Agent              │ Status    │ Current Task     │
├────────────────────┼───────────┼──────────────────┤
│ SpecWriter         │ ✓ Idle    │ -                │
│ DatabaseAdmin      │ ✓ Idle    │ -                │
│ BackendDeveloper   │ ⚙ Working │ Implement auth   │
│ FrontendDeveloper  │ ⏸ Waiting │ Need auth API    │
│ DevOps             │ ✓ Idle    │ -                │
└────────────────────┴───────────┴──────────────────┘
```

## Success Metrics

### Agent Performance

Track these metrics per agent:

- **Task Completion Rate**: % of assigned tasks completed successfully
- **Average Task Duration**: Time from assignment to completion
- **Collaboration Efficiency**: Time spent waiting on other agents
- **Error Rate**: % of tasks requiring human intervention
- **Test Pass Rate**: % of implementations passing tests first time

### System Performance

Track overall system metrics:

- **Feature Velocity**: Time from spec to deployed feature
- **Agent Utilization**: % of time agents are productively working
- **Handoff Efficiency**: Time for agent-to-agent handoffs
- **Rework Rate**: % of work requiring revision
- **Specification Quality**: % of specs implementable without clarification

## Troubleshooting Agent Issues

### Common Issues and Solutions

**Issue**: Frontend agent blocked waiting for Backend
- **Solution**: Backend prioritizes API contract delivery
- **Prevention**: API contracts defined upfront by SpecWriter

**Issue**: Database schema doesn't match spec
- **Solution**: DatabaseAdmin reviews spec, updates schema
- **Prevention**: SpecWriter validates data model completeness

**Issue**: Agents have conflicting requirements
- **Solution**: SpecWriter mediates, clarifies spec
- **Prevention**: Clear acceptance criteria in spec

**Issue**: Agent produces non-working code
- **Solution**: Agent reviews relevant skills, reruns with fixes
- **Prevention**: Better test coverage, clearer success criteria

## Agent Onboarding Checklist

When adding a new agent:

- [ ] Define agent ID and domain
- [ ] List responsibilities (primary and secondary)
- [ ] Assign skills the agent can execute
- [ ] Define decision-making authority
- [ ] Document interfaces (inputs/outputs)
- [ ] Create communication protocol examples
- [ ] Define success criteria
- [ ] Write example workflows
- [ ] Update collaboration patterns
- [ ] Add to status monitoring
- [ ] Document handoff procedures

## Appendix: Agent Quick Reference

| Agent ID | Name | Domain | Key Skills | Depends On |
|----------|------|--------|------------|------------|
| SPEC-001 | SpecWriter | Specs, docs | DOC-002 | User input |
| DATABASE-001 | DatabaseAdmin | Schema, migrations | DB-001-004 | SpecWriter |
| BACKEND-001 | BackendDeveloper | API endpoints | BE-001-005, AUTH-* | SpecWriter, DatabaseAdmin |
| FRONTEND-001 | FrontendDeveloper | UI, components | FE-001-006 | SpecWriter, BackendDeveloper |
| DEVOPS-001 | DevOps | Environment, deployment | DEVOPS-* | All agents |

---

## Document Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-12-17 | Initial sub-agents definition | Claude Sonnet 4.5 |
