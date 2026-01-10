<!--
Sync Impact Report:
Version: 0.1.0 → 1.0.0 (MAJOR - Initial constitution ratification)
Modified Principles: N/A (initial creation)
Added Sections:
  - Core Principles (8 principles covering event-driven architecture, microservices, observability, testing, security, infrastructure-as-code, deployment strategy, Dapr/Kafka integration)
  - Non-Functional Requirements
  - Development Workflow
  - Governance
Removed Sections: N/A
Templates Status:
  ✅ .specify/templates/spec-template.md - Compatible (user stories align with microservices architecture)
  ✅ .specify/templates/plan-template.md - Compatible (constitution check gates established)
  ✅ .specify/templates/tasks-template.md - Compatible (task organization supports event-driven implementation)
  ✅ .specify/templates/phr-template.prompt.md - Compatible (no changes needed)
Follow-up TODOs: None
-->

# Todo Chatbot Phase V: Advanced Cloud Deployment Constitution

## Core Principles

### I. Event-Driven Architecture (MANDATORY)

All task operations (create, update, complete, delete) MUST publish events to Kafka topics. Services MUST communicate through events rather than direct API calls. This enables loose coupling, scalability, and independent service deployment.

**Kafka Topic Requirements**:
- `task-events`: All CRUD operations on tasks (producer: Chat API, consumers: Recurring Task Service, Audit Service)
- `reminders`: Scheduled reminder triggers (producer: Chat API, consumer: Notification Service)
- `task-updates`: Real-time client synchronization (producer: Chat API, consumer: WebSocket Service)

**Event Schema Requirements**:
- Every event MUST include: `event_type`, `task_id`, `user_id`, `timestamp`
- Events MUST be immutable after publication
- Event schemas MUST be versioned and backward-compatible

**Rationale**: Event-driven architecture decouples services, enables audit trails, supports real-time features (reminders, recurring tasks), and scales better than synchronous request/response patterns.

### II. Microservices Independence (MANDATORY)

Each service (Chat API, Notification Service, Recurring Task Service, Audit Service) MUST be independently deployable, testable, and scalable. Services MUST NOT share databases or internal state.

**Service Boundaries**:
- **Chat API + MCP Tools**: User interaction, task CRUD operations, event publishing
- **Notification Service**: Consumes reminder events, sends notifications to users
- **Recurring Task Service**: Consumes task completion events, creates next occurrences
- **Audit Service**: Consumes all task events, maintains complete history

**Requirements**:
- Each service MUST have its own Dockerfile and Kubernetes Deployment
- Each service MUST expose health check endpoints (`/health`, `/ready`)
- Services MUST communicate via Dapr sidecar APIs (Pub/Sub, State, Service Invocation)
- Services MUST handle partial failures gracefully (circuit breakers, retries via Dapr)

**Rationale**: Microservices enable parallel development, independent scaling, fault isolation, and technology diversity while reducing blast radius of failures.

### III. Dapr for Infrastructure Abstraction (MANDATORY)

All infrastructure concerns (Kafka, database, secrets, service discovery, scheduling) MUST be abstracted through Dapr building blocks. Application code MUST NOT import Kafka clients, database drivers, or secret management libraries directly.

**Dapr Building Blocks Usage**:
- **Pub/Sub API**: Publish/subscribe to Kafka topics via HTTP (replaces `kafka-python`)
- **State Management API**: Store conversation state via HTTP (replaces direct DB calls)
- **Service Invocation API**: Service-to-service calls with automatic discovery, retries, mTLS
- **Jobs API**: Schedule exact-time reminders (replaces cron polling)
- **Secrets API**: Access Kubernetes secrets securely (replaces env vars in code)

**Example (Forbidden Direct Usage)**:
```python
# ❌ FORBIDDEN: Direct Kafka client
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers="kafka:9092")
producer.send("task-events", event)
```

**Example (Required Dapr Usage)**:
```python
# ✅ REQUIRED: Dapr Pub/Sub API
await httpx.post(
    "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
    json=event
)
```

**Rationale**: Dapr provides vendor-agnostic infrastructure abstraction, enabling portability (swap Kafka for RabbitMQ with config change), built-in resilience (retries, circuit breakers), and reduced application complexity.

### IV. Advanced Features Implementation (MANDATORY)

All advanced and intermediate level features MUST be implemented as specified:

**Advanced Features (P1)**:
- **Recurring Tasks**: When a recurring task is marked complete, publish `task.completed` event; Recurring Task Service consumes and auto-creates next occurrence based on recurrence pattern (daily, weekly, monthly)
- **Due Dates & Reminders**: When task with due date is created, schedule reminder using Dapr Jobs API; Notification Service publishes to `reminders` topic at scheduled time

**Intermediate Features (P2)**:
- **Priorities**: Tasks must support priority levels (High, Medium, Low)
- **Tags**: Tasks must support multiple tags for categorization
- **Search**: Full-text search across task titles and descriptions
- **Filter**: Filter tasks by status, priority, tags, due date ranges
- **Sort**: Sort tasks by created date, due date, priority, title

**Acceptance Criteria**:
- Each feature MUST be independently testable
- Each feature MUST publish appropriate events to Kafka
- Features MUST work in both local (Minikube) and cloud (AKS/GKE) deployments

**Rationale**: These features represent the core value proposition of Phase V and differentiate it from basic CRUD operations in earlier phases.

### V. Test-Driven Development for Critical Paths (MANDATORY)

Event flows, Dapr integrations, and Kafka message handling MUST follow TDD discipline: write tests → verify tests fail → implement → verify tests pass.

**Required Test Coverage**:
- **Contract Tests**: Verify event schemas match documented contracts (required for `task-events`, `reminders`, `task-updates` topics)
- **Integration Tests**: Test end-to-end flows (task creation → event published → consumer receives → side effect occurs)
- **Dapr Component Tests**: Verify Dapr sidecar interactions (pub/sub, state, jobs)
- **Failure Scenario Tests**: Test circuit breakers, retry logic, dead letter queues

**Test Organization**:
```
tests/
├── contract/           # Event schema validation
├── integration/        # End-to-end event flows
├── dapr/              # Dapr building block tests
└── unit/              # Business logic (optional)
```

**Rationale**: Event-driven systems are complex; TDD ensures event schemas are correct, consumers handle messages properly, and failure scenarios are covered before production deployment.

### VI. Observability and Distributed Tracing (MANDATORY)

All services MUST emit structured logs and metrics. Distributed tracing MUST be enabled via Dapr telemetry integration (OpenTelemetry).

**Logging Requirements**:
- All event publications MUST log: `event_type`, `task_id`, `user_id`, `timestamp`, `correlation_id`
- All event consumptions MUST log: `event_type`, `task_id`, `processing_status`, `correlation_id`
- Errors MUST log: `error_type`, `error_message`, `stack_trace`, `correlation_id`

**Metrics Requirements**:
- Event publication rates (events/second per topic)
- Event processing latency (time from publish to consume)
- Failed event processing count (for alerting)
- Dapr sidecar health metrics

**Tracing Requirements**:
- Dapr automatically injects `traceparent` headers following W3C Trace Context standard
- Services MUST propagate `traceparent` in outgoing requests
- Use Zipkin/Jaeger for trace visualization (deployed in Kubernetes)

**Rationale**: Distributed systems require comprehensive observability to debug event flows, identify bottlenecks, and troubleshoot failures across service boundaries.

### VII. Infrastructure as Code (MANDATORY)

All Kubernetes resources, Dapr components, Kafka topics, and configuration MUST be defined in version-controlled YAML files. Manual `kubectl` commands are FORBIDDEN except for debugging.

**Directory Structure**:
```
k8s/
├── helm-charts/todo-app/
│   ├── templates/
│   │   ├── deployments/        # Service deployments (Chat API, Notification, Recurring Task, Audit)
│   │   ├── services/           # K8s Services
│   │   ├── ingress/            # Ingress rules
│   │   ├── dapr-components/    # Dapr Pub/Sub, State, Secrets, Jobs
│   │   ├── kafka/              # Kafka cluster (Strimzi operator)
│   │   └── configmaps/         # Application configuration
│   ├── values.yaml             # Default values
│   ├── values-minikube.yaml    # Minikube-specific overrides
│   └── values-cloud.yaml       # AKS/GKE-specific overrides
└── strimzi/                    # Strimzi Kafka operator manifests
```

**Deployment Process**:
1. Install Strimzi operator: `kubectl apply -f k8s/strimzi/`
2. Deploy Kafka cluster: `helm install kafka k8s/helm-charts/kafka/`
3. Deploy Dapr components: `helm install todo-app k8s/helm-charts/todo-app/ --set dapr.enabled=true`
4. Deploy services: `helm install todo-app k8s/helm-charts/todo-app/`

**Rationale**: Infrastructure as Code ensures reproducible deployments, enables GitOps workflows, simplifies disaster recovery, and provides audit trail for infrastructure changes.

### VIII. Progressive Deployment Strategy (MANDATORY)

Deployments MUST follow a progressive rollout: Local (Minikube) → Cloud (AKS/GKE). Each environment MUST be validated before promoting to the next.

**Deployment Gates**:

**Local (Minikube) Gates**:
- All Docker images build successfully (< 500MB per image)
- Helm lint passes with zero warnings
- `helm install --dry-run` succeeds
- All pods reach `Running` state within 5 minutes
- Health checks return 200 OK for all services
- Event flow tests pass (publish → consume → side effect)
- Dapr sidecar injected and healthy for all pods

**Cloud (AKS/GKE) Gates**:
- All Minikube gates passed
- Kafka cluster (Redpanda Cloud or Strimzi) accessible
- Secrets configured in Kubernetes (OpenAI API key, Neon DB credentials)
- External database (Neon) reachable from cluster
- CI/CD pipeline (GitHub Actions) deploys successfully
- Load balancer provisions successfully
- External DNS resolves correctly
- Monitoring (Prometheus/Grafana) shows healthy metrics
- Distributed tracing (Zipkin/Jaeger) shows complete traces

**Rollback Requirements**:
- Previous Helm release MUST be retained (`helm rollback` tested)
- Database migrations MUST be backward-compatible
- Event schemas MUST be backward-compatible (consumers handle old and new formats)

**Rationale**: Progressive deployment reduces risk, enables early feedback in local environment, and ensures production readiness before cloud deployment.

## Non-Functional Requirements

### Performance Standards

- **Event Processing Latency**: p95 < 500ms from event publish to consumer processing
- **API Response Time**: p95 < 200ms for task CRUD operations
- **Reminder Accuracy**: Scheduled reminders fire within ±30 seconds of scheduled time
- **Concurrent Users**: Support 100 concurrent users on Minikube (1K+ on cloud)

### Reliability Standards

- **Service Availability**: 99.5% uptime for Chat API (excludes deployments)
- **Event Durability**: Zero message loss (Kafka replication factor ≥ 2 in cloud)
- **Graceful Degradation**: If Notification Service fails, task operations still succeed (event queued)
- **Retry Policy**: Failed event processing retried up to 3 times with exponential backoff

### Security Standards

- **Secrets Management**: All secrets (API keys, DB credentials) stored in Kubernetes Secrets, accessed via Dapr Secrets API
- **Service-to-Service Authentication**: Dapr mTLS enabled for all service invocations
- **Network Policies**: Services only accessible via Dapr sidecar (no direct pod-to-pod communication)
- **Image Security**: Docker images run as non-root user, no critical vulnerabilities (Docker Scout scan)

### Cost Management

- **Local Development**: Zero cost (Minikube, Redpanda Docker, Neon free tier)
- **Cloud Development**:
  - Oracle Cloud (Recommended): Always free tier (4 OCPUs, 24GB RAM) - unlimited duration
  - Azure AKS: $200 free credits (30 days) - migrate to Oracle if credits expire
  - Google GKE: $300 free credits (90 days) - migrate to Oracle if credits expire
- **Kafka**: Self-hosted Strimzi (compute-only cost) or Redpanda Cloud Serverless (free tier)

## Development Workflow

### Agentic Dev Stack Workflow (MANDATORY)

All feature development MUST follow this sequence:

1. **Specification** (`/sp.specify`): Write feature requirements in `specs/<feature>/spec.md`
2. **Planning** (`/sp.plan`): Generate architecture decisions in `specs/<feature>/plan.md`
3. **Task Breakdown** (`/sp.tasks`): Break into actionable tasks in `specs/<feature>/tasks.md`
4. **Implementation** (`/sp.implement`): Execute tasks via Claude Code (no manual coding)
5. **Review** (`/sp.analyze`): Cross-artifact consistency check
6. **ADR Creation** (`/sp.adr`): Document significant architectural decisions

**Validation Gates**:
- Spec MUST define user stories with priorities (P1, P2, P3)
- Plan MUST pass Constitution Check (verify compliance with all 8 principles)
- Tasks MUST map to user stories (traceability)
- ADRs MUST be created for: Event schema design, Dapr component selection, Kafka topic strategy, Service boundaries

### Prompt History Recording (MANDATORY)

Every user interaction MUST be recorded in a PHR (Prompt History Record) under `history/prompts/`:

**Routing Rules**:
- Constitution updates → `history/prompts/constitution/`
- Feature-specific work → `history/prompts/<feature-name>/`
- General queries → `history/prompts/general/`

**PHR Requirements**:
- All placeholders MUST be filled (no `{{TEMPLATE_VAR}}` left)
- Full user prompt MUST be preserved verbatim (no truncation)
- Representative response MUST be included
- Files created/modified MUST be listed
- Tests run MUST be listed

### Git Workflow

- **Branch Naming**: `<issue-number>-<feature-name>` (e.g., `5-recurring-tasks`)
- **Commit Messages**: `<type>: <description>` (e.g., `feat: add recurring task service`)
- **Commit Types**: `feat` (feature), `fix` (bug fix), `docs` (documentation), `refactor` (code refactor), `test` (tests), `chore` (maintenance)
- **PR Requirements**: All PRs MUST include: updated tasks.md (checkboxes), passing tests, updated README if user-facing changes

### CI/CD Pipeline (GitHub Actions)

**Trigger**: Push to `main` branch or PR creation

**Pipeline Stages**:
1. **Lint**: Helm lint all charts
2. **Build**: Build all Docker images, tag with commit SHA
3. **Test**: Run contract tests, integration tests
4. **Security Scan**: Docker Scout CVE scan (fail on critical vulnerabilities)
5. **Deploy to Staging** (on merge to `main`): Deploy to cloud staging environment
6. **Manual Approval**: Human approval required for production deployment
7. **Deploy to Production**: Helm upgrade with rollback on failure

## Governance

### Amendment Process

1. Propose amendment via ADR (`/sp.adr constitution-amendment-<topic>`)
2. Document rationale, alternatives considered, impact analysis
3. Review with stakeholders (team, instructor, peers)
4. Update constitution with new version number (semantic versioning)
5. Update dependent templates (spec, plan, tasks) if principle changes affect structure
6. Create PHR documenting amendment decision

### Versioning Policy

- **MAJOR**: Backward-incompatible governance changes (e.g., remove mandatory principle)
- **MINOR**: New principle added or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Review

- **Pre-Planning Review**: Plan template MUST include "Constitution Check" section validating all 8 principles
- **Pre-Implementation Review**: Tasks MUST reference constitution requirements (e.g., "T050: Implement Dapr Pub/Sub (Principle III)")
- **Pre-Deployment Review**: Helm charts MUST include Dapr sidecar annotations, Kafka component configs
- **Post-Implementation Review**: `/sp.analyze` MUST verify event schemas match documented contracts

### Complexity Justification

If any task requires violating constitution principles (e.g., direct Kafka client for debugging), it MUST be justified in plan.md "Complexity Tracking" table:

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Direct Kafka client in debug tool | Troubleshoot event delivery | Dapr Pub/Sub API insufficient for offset inspection |

### Reporting and Review

- Weekly: Review PHRs for patterns, blockers, recurring issues
- Sprint End: Review ADRs created, validate architectural alignment
- Phase End: Comprehensive constitution compliance audit

**Version**: 1.0.0 | **Ratified**: 2026-01-05 | **Last Amended**: 2026-01-05
