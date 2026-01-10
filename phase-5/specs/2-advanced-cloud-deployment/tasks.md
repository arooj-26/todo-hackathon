# Tasks: Advanced Cloud Deployment with Event-Driven Architecture

**Input**: Design documents from `specs/2-advanced-cloud-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are EXCLUDED from this list. The focus is on implementation following TDD principles where appropriate.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. MVP consists of Phase 1, 2, 3 (US1), 4 (US2), and 8 (US6).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a microservices architecture with:
- Backend services: `services/chat-api/`, `services/recurring-tasks/`, `services/notifications/`, `services/audit/`
- Frontend: `services/frontend/`
- Infrastructure: `k8s/helm-charts/todo-app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for microservices architecture

- [X] T001 Create microservices directory structure: services/{chat-api,recurring-tasks,notifications,audit,frontend}/
- [X] T002 [P] Initialize Chat API project with FastAPI 0.104+, SQLModel, httpx in services/chat-api/requirements.txt
- [X] T003 [P] Initialize Recurring Task Service with FastAPI in services/recurring-tasks/requirements.txt
- [X] T004 [P] Initialize Notification Service with FastAPI in services/notifications/requirements.txt
- [X] T005 [P] Initialize Audit Service with FastAPI in services/audit/requirements.txt
- [X] T006 [P] Initialize Next.js 14 frontend project in services/frontend/ with TypeScript, TanStack Query, Zustand
- [X] T007 [P] Create Dockerfiles for all 4 backend services with multi-stage builds (< 500MB target)
- [X] T008 [P] Create Dockerfile for frontend with Next.js production build
- [X] T009 [P] Create docker-compose.yml for local development with Kafka, PostgreSQL, Dapr sidecars
- [X] T010 [P] Configure Python linting (ruff) and formatting (black) for backend services
- [X] T011 [P] Configure ESLint and Prettier for frontend TypeScript code
- [X] T012 Create .env.example files for each service with required environment variables
- [X] T013 [P] Create initial project README.md with architecture overview and quickstart link

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Dapr Infrastructure

- [X] T014 Create database schema SQL in services/chat-api/migrations/001_initial_schema.sql (users, tasks, recurrence_patterns, reminders, tags, task_tags, audit_logs tables)
- [X] T015 [P] Setup Alembic migrations framework in services/chat-api/alembic.ini
- [X] T016 [P] Create Dapr component for Kafka Pub/Sub in k8s/helm-charts/todo-app/templates/dapr-components/kafka-pubsub.yaml
- [X] T017 [P] Create Dapr component for PostgreSQL State Store in k8s/helm-charts/todo-app/templates/dapr-components/statestore.yaml
- [X] T018 [P] Create Dapr component for Kubernetes Secrets in k8s/helm-charts/todo-app/templates/dapr-components/secrets.yaml
- [X] T019 [P] Create Strimzi Kafka cluster manifest in k8s/kafka/kafka-cluster.yaml (3 partitions, replication factor 2)
- [X] T020 [P] Create Kafka topics manifest in k8s/kafka/kafka-topics.yaml (task-events, reminders, task-updates)

### Shared Backend Models & Utilities

- [X] T021 [P] Create User model with timezone and notification preferences in services/chat-api/src/models/user.py
- [X] T022 [P] Create Task model with status, priority, due_at, search_vector in services/chat-api/src/models/task.py
- [X] T023 [P] Create RecurrencePattern model with pattern_type, interval, days_of_week in services/chat-api/src/models/recurrence.py
- [X] T024 [P] Create Tag and TaskTag models in services/chat-api/src/models/tag.py
- [X] T025 [P] Create Reminder model with remind_at, delivery_status in services/chat-api/src/models/reminder.py
- [X] T026 [P] Create AuditLog model in services/audit/src/models/audit_log.py
- [X] T027 [P] Create Dapr Pub/Sub client wrapper in services/chat-api/src/dapr/pubsub.py (publish method with correlation_id)
- [X] T028 [P] Create Dapr State API client wrapper in services/chat-api/src/dapr/state.py (get/set methods)
- [X] T029 [P] Create Dapr Secrets API client wrapper in services/chat-api/src/dapr/secrets.py (get_secret method)
- [X] T030 [P] Create TaskEvent schema with schema_version, event_type, task_snapshot in services/chat-api/src/events/task_event.py
- [X] T031 [P] Create ReminderEvent schema in services/chat-api/src/events/reminder_event.py
- [X] T032 [P] Create TaskUpdateEvent schema in services/chat-api/src/events/task_update_event.py
- [X] T033 Create database connection manager with Neon PostgreSQL config in services/chat-api/src/database.py
- [X] T034 [P] Create structured logging setup with correlation_id in services/chat-api/src/logging_config.py
- [X] T035 [P] Create error handling middleware for FastAPI in services/chat-api/src/middleware/error_handler.py
- [X] T036 [P] Create health check endpoint (/health, /ready) in services/chat-api/src/api/health.py

### Frontend Foundation

- [X] T037 [P] Create API client with fetch wrapper in services/frontend/src/lib/api.ts
- [X] T038 [P] Setup TanStack Query provider in services/frontend/src/app/providers.tsx
- [X] T039 [P] Create Zustand store for client state in services/frontend/src/lib/store.ts
- [X] T040 [P] Create base TaskList component skeleton in services/frontend/src/components/TaskList.tsx
- [X] T041 [P] Create base layout with navigation in services/frontend/src/app/layout.tsx
- [X] T042 [P] Configure Tailwind CSS with design tokens in services/frontend/tailwind.config.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Recurring Tasks Automation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks that automatically repeat on a schedule. When a recurring task is marked complete, the system automatically creates the next instance with the calculated due date.

**Independent Test**: Create a daily recurring task "Daily Standup", mark it complete today, verify a new instance is automatically created with tomorrow's date. Task history shows completed instance and new instance separately.

### Chat API Implementation for US1

- [X] T043 [P] [US1] Implement recurrence calculator service with python-dateutil rrule in services/chat-api/src/services/recurrence_calculator.py
- [X] T044 [US1] Implement TaskService.create_task() with recurrence pattern handling in services/chat-api/src/services/task_service.py
- [X] T045 [US1] Implement TaskService.complete_task() with event publishing in services/chat-api/src/services/task_service.py
- [X] T046 [US1] Create POST /tasks endpoint with recurrence_pattern in request body in services/chat-api/src/api/tasks.py
- [X] T047 [US1] Create POST /tasks/{id}/complete endpoint in services/chat-api/src/api/tasks.py
- [X] T048 [US1] Create GET /tasks endpoint with query filters in services/chat-api/src/api/tasks.py
- [X] T049 [US1] Add validation for recurrence pattern fields (pattern_type, interval, days_of_week) in services/chat-api/src/api/tasks.py
- [X] T050 [US1] Implement event publishing to task-events topic on task create/complete in services/chat-api/src/services/task_service.py

### Recurring Task Service Implementation for US1

- [X] T051 [P] [US1] Create Dapr subscription configuration for task-events topic in services/recurring-tasks/src/main.py (/dapr/subscribe endpoint)
- [X] T052 [US1] Implement task completed event handler with filter for recurring tasks in services/recurring-tasks/src/consumers/task_completed_handler.py
- [X] T053 [US1] Implement next due date calculator using rrule in services/recurring-tasks/src/services/recurrence_calculator.py
- [X] T054 [US1] Implement Chat API service invocation to create next task instance in services/recurring-tasks/src/services/task_creator.py
- [X] T055 [US1] Add logging for recurring task generation with correlation_id in services/recurring-tasks/src/consumers/task_completed_handler.py
- [X] T056 [US1] Implement end condition checking (never/after_occurrences/by_date) in services/recurring-tasks/src/services/recurrence_calculator.py

### Frontend Implementation for US1

- [X] T057 [P] [US1] Create RecurrencePatternForm component with pattern type selector in services/frontend/src/components/RecurrencePatternForm.tsx
- [X] T058 [P] [US1] Create useTasks hook with createTask, completeTask mutations in services/frontend/src/hooks/useTasks.ts
- [X] T059 [US1] Add recurrence pattern fields to TaskForm component in services/frontend/src/components/TaskForm.tsx
- [X] T060 [US1] Implement task completion UI with next instance notification in services/frontend/src/components/TaskList.tsx
- [X] T061 [US1] Add task history view showing completed recurring instances in services/frontend/src/components/TaskHistory.tsx
- [X] T062 [US1] Add "Stop Recurrence" button to recurring tasks in services/frontend/src/components/TaskList.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - recurring tasks create, complete, and auto-generate next instances

---

## Phase 4: User Story 2 - Due Dates and Automated Reminders (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign due dates to tasks and receive automated reminders at scheduled times before the due date without manually checking their task list.

**Independent Test**: Create a task "Submit Report" with due date tomorrow at 2pm and reminder 1 hour before. Verify user receives notification tomorrow at 1pm. Task shows "Due in 1 hour" status.

### Chat API Implementation for US2

- [X] T063 [P] [US2] Implement ReminderService with Dapr Jobs API integration in services/chat-api/src/services/reminder_service.py
- [X] T064 [US2] Add due_at and reminder_offset_minutes fields to POST /tasks endpoint in services/chat-api/src/api/tasks.py
- [X] T065 [US2] Implement schedule_reminder() method to create Dapr Job in services/chat-api/src/services/reminder_service.py
- [X] T066 [US2] Implement cancel_reminders() on task completion in services/chat-api/src/services/task_service.py
- [X] T067 [US2] Implement reschedule_reminders() on due date update in services/chat-api/src/services/task_service.py
- [X] T068 [US2] Add reminder records to database on scheduling in services/chat-api/src/services/reminder_service.py
- [X] T069 [US2] Create GET /tasks/{id}/reminders endpoint in services/chat-api/src/api/tasks.py

### Notification Service Implementation for US2

- [X] T070 [P] [US2] Create Dapr Jobs API callback endpoint (/jobs/reminder-trigger) in services/notifications/src/main.py
- [X] T071 [US2] Implement reminder trigger handler in services/notifications/src/jobs/reminder_trigger.py
- [X] T072 [US2] Implement notification dispatcher with multiple channels (in_app, email, SMS) in services/notifications/src/services/notification_dispatcher.py
- [X] T073 [US2] Publish ReminderEvent to reminders topic on trigger in services/notifications/src/jobs/reminder_trigger.py
- [X] T074 [US2] Implement retry logic for failed notification delivery in services/notifications/src/services/notification_dispatcher.py
- [X] T075 [US2] Add logging for reminder delivery with user_id and task_id in services/notifications/src/jobs/reminder_trigger.py

### Frontend Implementation for US2

- [X] T076 [P] [US2] Create DateTimePicker component for due date selection in services/frontend/src/components/DateTimePicker.tsx
- [X] T077 [P] [US2] Create ReminderOffsetSelector component (1 day, 1 hour, 15 min, custom) in services/frontend/src/components/ReminderOffsetSelector.tsx
- [X] T078 [US2] Add due_at and reminder fields to TaskForm in services/frontend/src/components/TaskForm.tsx
- [X] T079 [US2] Implement "Due in X hours/days" badge in TaskList in services/frontend/src/components/TaskList.tsx
- [X] T080 [US2] Create in-app notification display component in services/frontend/src/components/NotificationBanner.tsx
- [X] T081 [US2] Add reminder management UI to task detail view in services/frontend/src/components/TaskDetail.tsx

**Checkpoint**: At this point, User Story 2 should be fully functional - tasks have due dates, reminders schedule and fire, notifications deliver

---

## Phase 5: User Story 3 - Task Organization with Priorities and Tags (Priority: P2)

**Goal**: Enable users to organize tasks by priority levels (High/Medium/Low) and apply multiple tags for categorization to quickly find and focus on important work.

**Independent Test**: Create 5 tasks with different priorities and tags. Filter by "High priority + backend" and verify only matching tasks appear. Sort by priority and verify High tasks appear first.

### Chat API Implementation for US3

- [X] T082 [P] [US3] Implement TagService with create, list, autocomplete methods in services/chat-api/src/services/tag_service.py
- [X] T083 [US3] Create POST /tags endpoint in services/chat-api/src/api/tags.py
- [X] T084 [US3] Create GET /tags endpoint with search param for autocomplete in services/chat-api/src/api/tags.py
- [X] T085 [US3] Add tag_names array to POST /tasks and PATCH /tasks/{id} in services/chat-api/src/api/tasks.py
- [X] T086 [US3] Implement tag association logic in TaskService.create_task() in services/chat-api/src/services/task_service.py
- [X] T087 [US3] Add priority filter to GET /tasks endpoint in services/chat-api/src/api/tasks.py
- [X] T088 [US3] Add tags filter to GET /tasks endpoint (supports multiple tags) in services/chat-api/src/api/tasks.py
- [X] T089 [US3] Implement tag usage count calculation for autocomplete ranking in services/chat-api/src/services/tag_service.py

### Frontend Implementation for US3

- [X] T090 [P] [US3] Create PrioritySelector component with High/Medium/Low options in services/frontend/src/components/PrioritySelector.tsx
- [X] T091 [P] [US3] Create TagInput component with autocomplete in services/frontend/src/components/TagInput.tsx
- [X] T092 [P] [US3] Create useTags hook with getTags, createTag mutations in services/frontend/src/hooks/useTags.ts
- [X] T093 [US3] Add priority and tags fields to TaskForm in services/frontend/src/components/TaskForm.tsx
- [X] T094 [US3] Implement priority badge with color coding in TaskList in services/frontend/src/components/TaskList.tsx
- [X] T095 [US3] Implement tag pills with click-to-filter in TaskList in services/frontend/src/components/TaskList.tsx
- [X] T096 [US3] Create FilterPanel component with priority and tag filters in services/frontend/src/components/FilterPanel.tsx

**Checkpoint**: At this point, User Story 3 should be fully functional - tasks have priorities and tags, filtering and autocomplete work

---

## Phase 6: User Story 4 - Advanced Search and Filtering (Priority: P2)

**Goal**: Enable users to search tasks by text across titles and descriptions, and apply multiple filters simultaneously to quickly locate specific tasks among hundreds of entries.

**Independent Test**: Create 50 tasks with varied attributes. Search "presentation" and verify only matching tasks appear. Apply filters "High priority + due this week + incomplete" and verify results match all criteria.

### Chat API Implementation for US4

- [X] T097 [P] [US4] Implement SearchService with PostgreSQL full-text search (tsvector) in services/chat-api/src/services/search_service.py
- [X] T098 [US4] Add search query parameter to GET /tasks endpoint in services/chat-api/src/api/tasks.py
- [X] T099 [US4] Implement tsquery generation for search terms in services/chat-api/src/services/search_service.py
- [X] T100 [US4] Add status filter to GET /tasks endpoint in services/chat-api/src/api/tasks.py
- [X] T101 [US4] Add due_date_start and due_date_end filters to GET /tasks endpoint in services/chat-api/src/api/tasks.py
- [X] T102 [US4] Implement combined filter SQL query builder in services/chat-api/src/services/search_service.py
- [X] T103 [US4] Add pagination (limit, offset) to GET /tasks endpoint in services/chat-api/src/api/tasks.py
- [X] T104 [US4] Optimize query with proper index usage (search_vector GIN index) in services/chat-api/src/services/search_service.py

### Frontend Implementation for US4

- [X] T105 [P] [US4] Create SearchBar component with debounced input in services/frontend/src/components/SearchBar.tsx
- [X] T106 [P] [US4] Create StatusFilter component (todo/in_progress/completed) in services/frontend/src/components/StatusFilter.tsx
- [X] T107 [P] [US4] Create DateRangeFilter component for due date filtering in services/frontend/src/components/DateRangeFilter.tsx
- [X] T108 [P] [US4] Create useSearch hook with search and filter state in services/frontend/src/hooks/useSearch.ts
- [X] T109 [US4] Integrate SearchBar into main layout in services/frontend/src/app/layout.tsx
- [X] T110 [US4] Integrate FilterPanel with all filter components in services/frontend/src/components/FilterPanel.tsx
- [X] T111 [US4] Implement pagination controls in TaskList in services/frontend/src/components/TaskList.tsx
- [X] T112 [US4] Add "Clear all filters" button in services/frontend/src/components/FilterPanel.tsx

**Checkpoint**: At this point, User Story 4 should be fully functional - search works across text, multiple filters combine, pagination handles large result sets

---

## Phase 7: User Story 5 - Multi-Criteria Sorting (Priority: P3)

**Goal**: Enable users to sort task lists by multiple criteria (created date, due date, priority, title) in ascending or descending order.

**Independent Test**: Create 20 tasks with different due dates and priorities. Sort by "due date ascending" and verify earliest due date appears first. Switch to "priority descending + due date ascending" and verify High priority tasks with earliest due dates appear first.

### Chat API Implementation for US5

- [X] T113 [US5] Add sort parameter to GET /tasks endpoint (priority_asc/desc, due_date_asc/desc, created_asc/desc, title_asc/desc) in services/chat-api/src/api/tasks.py
- [X] T114 [US5] Implement SQL ORDER BY builder for sort options in services/chat-api/src/services/search_service.py
- [X] T115 [US5] Implement compound sorting (e.g., priority desc, then due_date asc) in services/chat-api/src/services/search_service.py

### Frontend Implementation for US5

- [X] T116 [P] [US5] Create SortSelector component with dropdown for sort options in services/frontend/src/components/SortSelector.tsx
- [X] T117 [US5] Add sort controls to TaskList header in services/frontend/src/components/TaskList.tsx
- [X] T118 [US5] Implement sort state persistence in URL params in services/frontend/src/hooks/useSearch.ts

**Checkpoint**: At this point, User Story 5 should be fully functional - sorting works by all criteria, compound sorts work

---

## Phase 8: User Story 6 - Progressive Deployment to Cloud (Priority: P1) 🎯 MVP

**Goal**: Enable deployment first to local Minikube for testing, then promote to cloud production environments (AKS/GKE/OKE) with confidence.

**Independent Test**: Deploy system to Minikube, verify all services running and health checks passing. Deploy same configuration to cloud staging, verify identical behavior. Promote to production, confirm zero downtime.

### Local Development (Minikube) Deployment

- [X] T119 [P] [US6] Create Helm chart structure in k8s/helm-charts/todo-app/ with Chart.yaml and values.yaml
- [X] T120 [P] [US6] Create Chat API deployment template in k8s/helm-charts/todo-app/templates/deployments/chat-api.yaml with Dapr annotations
- [X] T121 [P] [US6] Create Recurring Task Service deployment template in k8s/helm-charts/todo-app/templates/deployments/recurring-tasks.yaml
- [X] T122 [P] [US6] Create Notification Service deployment template in k8s/helm-charts/todo-app/templates/deployments/notifications.yaml
- [X] T123 [P] [US6] Create Audit Service deployment template in k8s/helm-charts/todo-app/templates/deployments/audit.yaml
- [X] T124 [P] [US6] Create Frontend deployment template in k8s/helm-charts/todo-app/templates/deployments/frontend.yaml
- [X] T125 [P] [US6] Create Kubernetes Services for all deployments in k8s/helm-charts/todo-app/templates/services/
- [X] T126 [P] [US6] Create ConfigMaps for application config in k8s/helm-charts/todo-app/templates/configmaps/
- [X] T127 [P] [US6] Create Secrets templates for database connection, JWT secret in k8s/helm-charts/todo-app/templates/secrets/
- [X] T128 [P] [US6] Create values-minikube.yaml with local overrides (NodePort services, resource limits)
- [X] T129 [P] [US6] Create PodDisruptionBudget for zero-downtime deployments in k8s/helm-charts/todo-app/templates/pdb/
- [X] T130 [US6] Create Minikube deployment script in k8s/scripts/deploy-minikube.sh (Dapr init, Strimzi install, Helm install)
- [X] T131 [US6] Create validation script to check all pods running in k8s/scripts/validate-deployment.sh
- [X] T132 [US6] Update quickstart.md with Minikube deployment instructions in specs/2-advanced-cloud-deployment/quickstart.md

### Cloud Deployment (AKS/GKE/OKE)

- [X] T133 [P] [US6] Create values-cloud.yaml with cloud overrides (LoadBalancer services, HPA, PVC) in k8s/helm-charts/todo-app/
- [X] T134 [P] [US6] Create HorizontalPodAutoscaler for all services in k8s/helm-charts/todo-app/templates/hpa/
- [X] T135 [P] [US6] Create Ingress configuration with NGINX in k8s/helm-charts/todo-app/templates/ingress/
- [X] T136 [P] [US6] Create cloud-specific Dapr components (managed Kafka if using Redpanda Cloud) in k8s/helm-charts/todo-app/templates/dapr-components/
- [X] T137 [US6] Create cloud deployment script for AKS in k8s/scripts/deploy-aks.sh
- [X] T138 [US6] Create cloud deployment script for GKE in k8s/scripts/deploy-gke.sh
- [X] T139 [US6] Create cloud deployment script for OKE in k8s/scripts/deploy-oke.sh
- [X] T140 [US6] Create rollback script with Helm in k8s/scripts/rollback.sh
- [X] T141 [US6] Document cloud deployment process in specs/2-advanced-cloud-deployment/cloud-deployment.md

**Checkpoint**: At this point, User Story 6 should be fully functional - system deploys to Minikube and cloud, rollback works

---

## Phase 9: User Story 7 - Automated CI/CD Pipeline (Priority: P2)

**Goal**: Enable automated pipeline that builds, tests, and deploys code changes to staging automatically on commit, and to production after manual approval.

**Independent Test**: Push code change to main branch. Verify pipeline automatically builds Docker images, runs tests, deploys to staging. Approve production deployment, verify automatic rollout.

### GitHub Actions CI/CD

- [X] T142 [P] [US7] Create GitHub Actions workflow for build in .github/workflows/build.yml (build all Docker images, push to registry)
- [X] T143 [P] [US7] Create GitHub Actions workflow for staging deployment in .github/workflows/deploy-staging.yml (deploy to staging on main commit)
- [X] T144 [P] [US7] Create GitHub Actions workflow for production deployment in .github/workflows/deploy-production.yml (manual approval gate)
- [X] T145 [US7] Configure Docker image tagging strategy (git SHA + latest) in .github/workflows/build.yml
- [X] T146 [US7] Add health check validation step to deployment workflows in .github/workflows/deploy-staging.yml
- [X] T147 [US7] Add automatic rollback on failed health checks in .github/workflows/deploy-production.yml
- [X] T148 [US7] Configure GitHub Secrets for cloud credentials, database connection strings
- [X] T149 [US7] Add pipeline status badges to README.md
- [X] T150 [US7] Document CI/CD process in specs/2-advanced-cloud-deployment/cicd.md

**Checkpoint**: At this point, User Story 7 should be fully functional - CI/CD pipeline builds, tests, deploys to staging/production

---

## Phase 10: User Story 8 - Real-Time Monitoring and Observability (Priority: P2)

**Goal**: Enable operations teams to view service health metrics, distributed traces, and structured logs for debugging production issues.

**Independent Test**: Generate load on system (100 concurrent users). View monitoring dashboard showing request rate, latency percentiles, error rate. Drill into specific failed request to view complete distributed trace.

### Audit Service Implementation for US8

- [ ] T151 [P] [US8] Create Dapr subscription for task-events topic in services/audit/src/main.py
- [ ] T152 [US8] Implement task event handler to persist to audit_logs table in services/audit/src/consumers/task_event_handler.py
- [ ] T153 [US8] Create GET /audit-logs endpoint with filters in services/audit/src/api/audit.py
- [ ] T154 [US8] Add retention policy enforcement (90-day window) in services/audit/src/services/audit_service.py

### Observability Infrastructure

- [X] T155 [P] [US8] Add Prometheus metrics exporters to all services (/metrics endpoint) using FastAPI instrumentation
- [X] T156 [P] [US8] Define custom metrics: events_published_total, event_processing_duration_seconds, event_processing_failures_total
- [X] T157 [P] [US8] Configure Dapr to export spans to Zipkin in k8s/helm-charts/todo-app/templates/dapr-config/tracing.yaml
- [X] T158 [P] [US8] Create Prometheus deployment and config in k8s/monitoring/prometheus/
- [X] T159 [P] [US8] Create Grafana deployment in k8s/monitoring/grafana/
- [X] T160 [P] [US8] Create Zipkin deployment in k8s/monitoring/zipkin/
- [X] T161 [US8] Create Grafana dashboards for service health (CPU, memory, request rate, latency, error rate) in k8s/monitoring/grafana/dashboards/
- [X] T162 [US8] Create Grafana dashboard for event processing metrics in k8s/monitoring/grafana/dashboards/
- [X] T163 [US8] Configure Prometheus alerting rules for service health in k8s/monitoring/prometheus/alerts/
- [X] T164 [US8] Add structured logging with correlation_id to all event handlers
- [X] T165 [US8] Configure log aggregation with Loki (optional) in k8s/monitoring/loki/
- [X] T166 [US8] Document monitoring and troubleshooting in specs/2-advanced-cloud-deployment/monitoring.md

**Checkpoint**: At this point, User Story 8 should be fully functional - monitoring dashboard shows metrics, traces show request flows, logs are searchable

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T167 [P] Add API documentation with Swagger UI at /docs endpoint for Chat API
- [X] T168 [P] Add comprehensive error messages for all validation failures
- [X] T169 [P] Implement rate limiting for API endpoints to prevent abuse
- [X] T170 [P] Add request/response logging middleware to all services
- [X] T171 [P] Optimize Docker images to stay under 500MB target (multi-stage builds, slim base images)
- [X] T172 [P] Add security headers (CORS, CSP) to all API responses
- [X] T173 [P] Implement circuit breaker configuration for Dapr Service Invocation
- [X] T174 [P] Add retry policy configuration for Dapr Pub/Sub (3 attempts, exponential backoff)
- [X] T175 [P] Configure Dead Letter Queue for failed event processing
- [X] T176 Validate all deployment gates from constitution (local → staging → production)
- [X] T177 Run full end-to-end validation following quickstart.md
- [X] T178 Performance testing with Locust (1000 concurrent users, verify p95 < 200ms)
- [X] T179 Chaos testing: Restart Kafka broker, verify event processing recovers
- [X] T180 Security audit: Verify no secrets in source code, all credentials in secret stores

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - US1 Recurring Tasks (Phase 3): Can start after Foundational ✅ MVP
  - US2 Reminders (Phase 4): Can start after Foundational ✅ MVP
  - US3 Tags/Priorities (Phase 5): Can start after Foundational (integrates with US1/US2 tasks)
  - US4 Search/Filter (Phase 6): Can start after Foundational, enhanced by US3 tags
  - US5 Sorting (Phase 7): Can start after Foundational, minimal integration
  - US6 Deployment (Phase 8): BLOCKS production release - must complete for MVP ✅
  - US7 CI/CD (Phase 9): Can start after US6 deployment infrastructure exists
  - US8 Monitoring (Phase 10): Can start in parallel with other stories, critical for production
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Recurring Tasks)**: Independent - Can start after Foundational ✅ MVP CORE
- **US2 (Reminders)**: Independent - Can start after Foundational ✅ MVP CORE
- **US3 (Tags/Priorities)**: Independent - Can start after Foundational (enhances existing tasks)
- **US4 (Search/Filter)**: Light dependency on US3 (tag filtering), but can implement without
- **US5 (Sorting)**: Independent - Can start after Foundational
- **US6 (Deployment)**: Independent infrastructure work ✅ MVP REQUIRED
- **US7 (CI/CD)**: Depends on US6 (needs deployment infrastructure)
- **US8 (Monitoring)**: Independent - Can start in parallel ✅ MVP RECOMMENDED

### Critical Path for MVP

**Minimum Viable Product = US1 + US2 + US6 + US8 (partial)**

1. Phase 1: Setup (1-2 days)
2. Phase 2: Foundational (3-4 days) **← CRITICAL BLOCKER**
3. Phase 3: US1 Recurring Tasks (3-4 days)
4. Phase 4: US2 Reminders (3-4 days)
5. Phase 8: US6 Deployment (2-3 days) **← REQUIRED FOR PRODUCTION**
6. Phase 10: US8 Monitoring - Basic (1-2 days) **← PRODUCTION VISIBILITY**

**Total MVP Timeline**: ~14-19 days sequential, or ~7-10 days with 2-3 parallel developers

### Parallel Opportunities

**After Foundational Phase Completes, these can run in parallel:**

- Team A: Phase 3 (US1 Recurring Tasks)
- Team B: Phase 4 (US2 Reminders)
- Team C: Phase 5 (US3 Tags/Priorities)
- Team D: Phase 8 (US6 Deployment Infrastructure)
- Team E: Phase 10 (US8 Monitoring Setup)

**Within each phase:**
- All tasks marked [P] can run in parallel (different files, no dependencies)
- Models can be created in parallel
- Frontend and backend for same story can be worked on in parallel after contracts are defined

---

## Parallel Example: User Story 1 (Recurring Tasks)

```bash
# These tasks can run in parallel (different files):
T043 [P] Recurrence calculator service (services/chat-api/src/services/recurrence_calculator.py)
T051 [P] Dapr subscription config (services/recurring-tasks/src/main.py)
T057 [P] RecurrencePatternForm component (services/frontend/src/components/RecurrencePatternForm.tsx)
T058 [P] useTasks hook (services/frontend/src/hooks/useTasks.ts)

# Then these depend on above:
T044 TaskService.create_task() (needs T043 recurrence calculator)
T052 Task completed event handler (needs T051 subscription config)
T059 Add to TaskForm (needs T057 RecurrencePatternForm, T058 useTasks hook)
```

---

## Implementation Strategy

### MVP First (Recommended for Phase V)

**Goal**: Deploy working system to production ASAP with core value proposition

1. ✅ Complete Phase 1: Setup (all infrastructure scaffolding)
2. ✅ Complete Phase 2: Foundational (CRITICAL - blocks everything)
3. ✅ Complete Phase 3: US1 Recurring Tasks (core differentiator)
4. ✅ Complete Phase 4: US2 Reminders (completes productivity story)
5. ✅ Complete Phase 8: US6 Deployment (enables production deploy)
6. ✅ Complete Phase 10: US8 Monitoring (basic) (production visibility)
7. **STOP and VALIDATE**: Deploy to Minikube, test US1+US2 independently
8. **Deploy to Cloud Staging**: Validate in production-like environment
9. **Deploy to Cloud Production**: MVP is live!

**MVP Delivers**: Recurring tasks + reminders + cloud deployment + basic monitoring = Complete Phase V core value

### Incremental Delivery (Post-MVP)

After MVP is deployed and validated:

1. ✅ Add Phase 5: US3 Tags/Priorities → Deploy/Demo (better organization)
2. ✅ Add Phase 6: US4 Search/Filter → Deploy/Demo (scalability for large task lists)
3. ✅ Add Phase 7: US5 Sorting → Deploy/Demo (UX polish)
4. ✅ Add Phase 9: US7 CI/CD Pipeline → Deploy/Demo (operations efficiency)
5. ✅ Add Phase 10: US8 Monitoring (complete) → Deploy/Demo (full observability)
6. ✅ Complete Phase 11: Polish → Final production hardening

### Parallel Team Strategy (If 3-4 developers available)

**Sprint 1: Foundation (Everyone together)**
- All hands on Phase 1 + Phase 2 (~1 week)

**Sprint 2: Core MVP (Parallel work)**
- Developer A: Phase 3 (US1 Recurring Tasks)
- Developer B: Phase 4 (US2 Reminders)
- Developer C: Phase 8 (US6 Deployment)
- Developer D: Phase 10 (US8 Monitoring)
- ~1-2 weeks, then integrate

**Sprint 3: Integration & Deploy**
- Everyone: Integration testing, bug fixes
- Deploy to Minikube → Staging → Production
- MVP complete!

**Sprint 4+: Enhancements (Parallel work)**
- Developer A: Phase 5 (US3 Tags)
- Developer B: Phase 6 (US4 Search)
- Developer C: Phase 7 (US5 Sorting)
- Developer D: Phase 9 (US7 CI/CD), Phase 11 (Polish)

---

## Task Statistics

**Total Tasks**: 180
**Tasks by Priority**:
- P1 MVP Tasks: 89 tasks (Setup + Foundational + US1 + US2 + US6 + US8 basic)
- P2 Enhancement Tasks: 67 tasks (US3 + US4 + US7 + US8 complete)
- P3 Polish Tasks: 24 tasks (US5 + Phase 11)

**Tasks by Phase**:
- Phase 1 (Setup): 13 tasks
- Phase 2 (Foundational): 29 tasks
- Phase 3 (US1 Recurring): 20 tasks
- Phase 4 (US2 Reminders): 19 tasks
- Phase 5 (US3 Tags/Priorities): 16 tasks
- Phase 6 (US4 Search/Filter): 16 tasks
- Phase 7 (US5 Sorting): 6 tasks
- Phase 8 (US6 Deployment): 23 tasks
- Phase 9 (US7 CI/CD): 9 tasks
- Phase 10 (US8 Monitoring): 15 tasks
- Phase 11 (Polish): 14 tasks

**Parallelizable Tasks**: 98 tasks marked [P] (54% can run in parallel within their phase)

**Independent Test Criteria**:
- US1: Recurring task completes → next instance auto-created ✅
- US2: Task with due date → reminder fires at scheduled time ✅
- US3: Filter by priority+tags → only matching tasks shown ✅
- US4: Search + multiple filters → results match all criteria ✅
- US5: Sort by criteria → tasks ordered correctly ✅
- US6: Deploy Minikube → cloud → all services healthy ✅
- US7: Push code → pipeline deploys → production updated ✅
- US8: View dashboard → metrics shown → trace available ✅

---

## Notes

- Tasks are organized by user story for independent implementation and testing
- [P] marker indicates parallelizable tasks (different files, no dependencies)
- [Story] label (e.g., [US1]) maps task to specific user story for traceability
- MVP = Phases 1, 2, 3, 4, 8 (partial), 10 (partial) = ~89 tasks
- Each user story checkpoint verifies story works independently
- Constitution principles embedded: event-driven (US1/US2), Dapr abstraction (all), progressive deployment (US6), observability (US8)
- Zero test tasks included (not explicitly requested in spec, though TDD encouraged in constitution)
- All file paths follow microservices structure from plan.md
- Critical blocker: Phase 2 must complete before any user story work begins
- Deployment (US6) must complete before production release (MVP gate)
