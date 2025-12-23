# Multi-Agent Development System

A collaborative multi-agent system for autonomous full-stack application development.

## Overview

This system implements a **multi-agent architecture** where specialized AI agents collaborate to build full-stack applications. Each agent has specific skills and responsibilities, and they communicate through a message-passing system coordinated by an orchestrator.

## Architecture

### Agents

The system includes 5 specialized agents:

1. **FrontendDeveloper_Agent** (`FRONTEND-001`)
   - **Domain**: Next.js frontend, React components, UI/UX
   - **Skills**: FE-001 through FE-006, TEST-003
   - **Autonomy**: High within frontend domain
   - **Responsibilities**:
     - Initialize Next.js projects
     - Create React components
     - Implement Better Auth
     - Create API clients
     - Implement route protection
     - Apply TailwindCSS styling
     - Write frontend tests

2. **BackendDeveloper_Agent** (`BACKEND-001`)
   - **Domain**: FastAPI backend, API endpoints, business logic
   - **Skills**: BE-001 through BE-005, AUTH-001/002/003, TEST-001/002, DOC-001
   - **Autonomy**: High within backend domain
   - **Responsibilities**:
     - Initialize FastAPI projects
     - Define API endpoints
     - Implement JWT authentication
     - Configure CORS
     - Implement user-scoped data access
     - Write backend tests
     - Generate OpenAPI documentation

3. **DatabaseAdmin_Agent** (`DATABASE-001`)
   - **Domain**: Database schema, migrations, data access
   - **Skills**: DB-001 through DB-004
   - **Autonomy**: Medium (schema changes require approval)
   - **Responsibilities**:
     - Define database schemas with SQLModel
     - Configure Neon PostgreSQL connection
     - Create Alembic migrations
     - Create database indexes

4. **SpecWriter_Agent** (`SPEC-001`)
   - **Domain**: Specifications, documentation, requirements
   - **Skills**: DOC-002
   - **Autonomy**: Medium (gatekeeper for requirements)
   - **Responsibilities**:
     - Update specification documents
     - Maintain API contracts
     - Track implementation status

5. **DevOps_Agent** (`DEVOPS-001`)
   - **Domain**: Environment, deployment, infrastructure
   - **Skills**: DEVOPS-001, DEVOPS-002
   - **Autonomy**: Medium (infrastructure with oversight)
   - **Responsibilities**:
     - Create Docker Compose configuration
     - Configure environment variables
     - Create deployment documentation

### Skills Library

The system includes **30+ atomic skills** organized by category:

- **Frontend Development**: 6 skills (FE-001 to FE-006)
- **Backend Development**: 5 skills (BE-001 to BE-005)
- **Database Management**: 4 skills (DB-001 to DB-004)
- **Authentication & Security**: 3 skills (AUTH-001 to AUTH-003)
- **Testing & Validation**: 3 skills (TEST-001 to TEST-003)
- **Documentation**: 2 skills (DOC-001, DOC-002)
- **DevOps & Deployment**: 2 skills (DEVOPS-001, DEVOPS-002)

Each skill is:
- **Atomic**: Performs one specific task
- **Reusable**: Can be executed by any agent with the skill
- **Testable**: Has clear success criteria
- **Composable**: Can be combined into workflows

## Directory Structure

```
.agents/
├── agents/               # Agent implementations
│   ├── frontend_developer.py
│   ├── backend_developer.py
│   ├── database_admin.py
│   ├── spec_writer.py
│   └── devops.py
├── skills/              # Skill implementations
│   ├── frontend/        # Frontend skills (FE-001 to FE-006)
│   ├── backend/         # Backend skills (BE-001 to BE-005)
│   ├── database/        # Database skills (DB-001 to DB-004)
│   ├── auth/            # Auth skills (AUTH-001 to AUTH-003)
│   ├── testing/         # Testing skills (TEST-001 to TEST-003)
│   ├── docs/            # Documentation skills (DOC-001, DOC-002)
│   └── devops/          # DevOps skills (DEVOPS-001, DEVOPS-002)
├── lib/                 # Base frameworks
│   ├── agent_base.py    # Agent base classes and registry
│   └── skill_base.py    # Skill base classes and registry
├── logs/                # Agent message logs
├── orchestrator.py      # Multi-agent coordinator
└── README.md            # This file
```

## Usage

### Running the Orchestrator

The orchestrator coordinates multiple agents to complete complex workflows:

```python
from .agents.orchestrator import Orchestrator

# Import agents to register them
from .agents.agents import (
    frontend_agent,
    backend_agent,
    database_agent,
    spec_writer_agent,
    devops_agent
)

# Create orchestrator
orchestrator = Orchestrator()

# Create a workflow
workflow_id = orchestrator.create_feature_implementation_workflow()

# Execute workflow
result = orchestrator.execute_workflow(workflow_id)

print(f"Workflow Status: {result['status']}")
print(f"Completed Steps: {result['completed_steps']}")
```

### Running from Command Line

```bash
# Execute the orchestrator
cd .agents
python -m orchestrator

# Or run directly
python orchestrator.py
```

### Creating Custom Workflows

```python
from .agents.orchestrator import Orchestrator, WorkflowStep

orchestrator = Orchestrator()

# Define workflow steps
steps = [
    WorkflowStep(
        step_id="setup-backend",
        agent_id="BACKEND-001",
        description="Initialize FastAPI project",
        skills_required=["BE-001"],
        inputs={"BE-001": {"project_name": "backend"}},
        depends_on=[],
        priority="urgent"
    ),
    WorkflowStep(
        step_id="setup-frontend",
        agent_id="FRONTEND-001",
        description="Initialize Next.js project",
        skills_required=["FE-001"],
        inputs={"FE-001": {"project_name": "frontend"}},
        depends_on=["setup-backend"],
        priority="urgent"
    )
]

# Create and execute
workflow_id = orchestrator.create_workflow(
    name="Project Setup",
    description="Initialize full-stack project",
    steps=steps
)

result = orchestrator.execute_workflow(workflow_id)
```

### Executing Individual Skills

```python
from .agents.lib.skill_base import execute_skill

# Execute a skill directly
result = execute_skill(
    skill_id="FE-001",
    params={
        "project_name": "my-app",
        "use_typescript": True,
        "use_tailwind": True
    },
    context={
        "agent_id": "FRONTEND-001",
        "task_id": "init-project"
    }
)

print(f"Status: {result.status}")
print(f"Result: {result.result}")
print(f"Artifacts: {result.artifacts}")
```

### Checking Agent Status

```python
# Get all agents status
statuses = orchestrator.get_all_agents_status()

for status in statuses:
    print(f"{status['agent_name']}: {status['status']}")
    print(f"  Completed: {status['completed_tasks']}")
    print(f"  Failed: {status['failed_tasks']}")

# Get specific agent status
backend_status = orchestrator.get_agent_status("BACKEND-001")
```

## Communication Protocol

Agents communicate through message passing:

### Message Types

- **REQUEST**: Request information or action from another agent
- **RESPONSE**: Respond to a request
- **NOTIFICATION**: Broadcast information to other agents
- **ERROR**: Report errors to other agents

### Example Message

```python
{
    "message_id": "uuid",
    "from_agent": "BACKEND-001",
    "to_agent": "FRONTEND-001",
    "message_type": "notification",
    "topic": "api_ready",
    "payload": {
        "endpoints": ["/api/tasks", "/api/auth/signin"],
        "base_url": "http://localhost:8000"
    },
    "timestamp": "2025-12-17T10:30:00"
}
```

### Agent Communication Example

```python
# Backend agent notifies Frontend agent
backend_agent.send_message(
    to_agent="FRONTEND-001",
    message_type=MessageType.NOTIFICATION,
    topic="api_ready",
    payload={
        "endpoints": created_endpoints,
        "base_url": "http://localhost:8000"
    }
)
```

## Collaboration Patterns

### Pattern 1: Feature Implementation

1. **SpecWriter** creates/updates specification
2. **DatabaseAdmin** defines schema and migrations
3. **Backend** implements API endpoints
4. **Frontend** creates UI components
5. **DevOps** configures deployment

### Pattern 2: API Contract First

1. **SpecWriter** defines API contract
2. **Backend** and **Frontend** work in parallel:
   - Backend implements endpoints
   - Frontend creates API client
3. **Integration** when both complete

### Pattern 3: Schema Evolution

1. **Backend** requests schema changes
2. **DatabaseAdmin** evaluates and implements
3. **DatabaseAdmin** creates migration
4. **Backend** updates models
5. **Frontend** updates types if needed

## Decision-Making Authority

Each agent has explicit decision-making boundaries:

### Can Decide (Autonomous)
- Agent makes these decisions without consulting others
- Examples: Component structure, styling details, validation rules

### Must Consult (Collaborative)
- Agent must coordinate with other agents
- Examples: API contracts, schema changes, CORS configuration

### Cannot Decide (Blocked)
- Agent cannot make these decisions
- Examples: Business requirements, infrastructure choices

## Success Criteria

Each skill defines success criteria for validation:

```python
skill.get_success_criteria()
# Returns:
[
    "Project created in frontend/ directory",
    "package.json contains Next.js 16+",
    "TypeScript configuration present",
    "App Router structure (app/ directory)"
]
```

## Logging and Monitoring

### Agent Message Logs

All inter-agent messages are logged:

```
.agents/logs/
├── FRONTEND-001_messages.jsonl
├── BACKEND-001_messages.jsonl
├── DATABASE-001_messages.jsonl
├── SPEC-001_messages.jsonl
└── DEVOPS-001_messages.jsonl
```

### Viewing Logs

```bash
# View all messages from Backend agent
cat .agents/logs/BACKEND-001_messages.jsonl | jq '.'

# Filter by topic
cat .agents/logs/BACKEND-001_messages.jsonl | jq 'select(.topic=="api_ready")'
```

## Error Handling

### Skill Execution Errors

```python
if output.status == SkillStatus.FAILED:
    print(f"Skill failed: {output.error}")
    # Agent stops execution and reports failure
```

### Workflow Error Handling

- **Urgent steps**: Workflow stops on failure
- **Normal steps**: Workflow continues, marks step as failed
- **Partial completion**: Some steps succeed, some fail

## Testing

### Unit Testing Skills

```bash
cd .agents
pytest skills/backend/be001_init_fastapi.py -v
```

### Integration Testing Agents

```bash
pytest agents/backend_developer.py -v
```

### Testing Workflows

```bash
python orchestrator.py
```

## Contributing

### Adding a New Skill

1. Create skill file in appropriate category directory
2. Extend `Skill` base class
3. Implement required methods:
   - `metadata()`: Skill information
   - `validate_inputs()`: Input validation
   - `execute()`: Skill logic
   - `get_success_criteria()`: Success checklist
4. Register skill with `@register_skill` decorator

Example:

```python
from ...lib.skill_base import Skill, register_skill

@register_skill
class MyNewSkill(Skill):
    @property
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            skill_id="CAT-001",
            name="My New Skill",
            description="Does something useful",
            category="category",
            version="1.0.0",
            dependencies=[],
            inputs_schema={...},
            outputs_schema={...}
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        # Validation logic
        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        # Execution logic
        return SkillOutput(status=SkillStatus.SUCCESS, ...)

    def get_success_criteria(self) -> List[str]:
        return ["Criterion 1", "Criterion 2"]
```

### Adding a New Agent

1. Create agent file in `agents/` directory
2. Extend `Agent` base class
3. Implement required methods:
   - `config()`: Agent configuration
   - `plan_task()`: Task planning logic
   - `execute_task()`: Task execution logic
4. Register agent with `register_agent()`

## Troubleshooting

### Agent Not Found

```python
# Ensure agent is imported and registered
from .agents.agents import backend_agent

# Check registry
from .lib.agent_base import agent_registry
print(agent_registry.list_all())
```

### Skill Not Found

```python
# Ensure skill is imported
from .skills.backend import be001_init_fastapi

# Check registry
from .lib.skill_base import skill_registry
print(skill_registry.list_all())
```

### Circular Dependencies

- Workflow orchestrator detects circular dependencies
- Check `depends_on` in workflow steps
- Ensure proper step ordering

## Future Enhancements

- [ ] Async skill execution for parallel work
- [ ] Real message bus (RabbitMQ, Redis) instead of logging
- [ ] Agent learning from execution history
- [ ] Dynamic skill discovery and loading
- [ ] Web dashboard for monitoring agents
- [ ] Agent performance metrics and optimization
- [ ] Rollback mechanisms for failed workflows
- [ ] Agent capability negotiation

## License

See project root LICENSE file.
