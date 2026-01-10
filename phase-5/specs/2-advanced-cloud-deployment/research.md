# Research: Advanced Cloud Deployment Technology Decisions

**Feature**: Advanced Cloud Deployment with Event-Driven Architecture
**Date**: 2026-01-05
**Status**: Complete

## Executive Summary

This document consolidates research findings for 10 critical technology decisions required for Phase V implementation. All decisions prioritize constitution compliance (event-driven architecture, Dapr abstraction, progressive deployment) while optimizing for hackathon/learning environment constraints (zero-cost cloud options, rapid iteration).

**Key Decisions**:
1. JSON Schema with version field for event versioning (simplicity, no external dependencies)
2. Dapr Jobs API with PostgreSQL persistence (exactly-once reminders, survives pod restarts)
3. Partition Kafka by task_id using murmur2 hash (ordering per task, parallel processing)
4. PostgreSQL GIN index on tsvector (sub-second search for 10k tasks)
5. dateutil.rrule for recurrence calculation (battle-tested, iCalendar standard)
6. Dapr retry policy 3x with exponential backoff, circuit breaker after 5 failures
7. Helm rolling updates with PodDisruptionBudget and readiness gates (zero downtime)
8. 10% trace sampling for production, 100% for development (cost/visibility tradeoff)
9. Dapr DLQ with max 3 retries, Prometheus alert on DLQ depth >10
10. HPA on custom metric: Kafka consumer lag >100 messages → scale up

---

## 1. Event Schema Versioning Strategy

### Decision: JSON Schema with Embedded Version Field

**Rationale**:
- Simplest approach for hackathon timeline - no external schema registry infrastructure
- Backward compatibility enforced through Pydantic validators at code level
- Version field in every event enables consumers to handle multiple versions gracefully

**Implementation**:
```python
# Base event schema (all events inherit)
class BaseEvent(BaseModel):
    schema_version: Literal["1.0"] = "1.0"  # Incremented on breaking changes
    event_type: str
    task_id: int
    user_id: str
    timestamp: datetime
    correlation_id: str

# Specific event schema
class TaskEvent(BaseEvent):
    event_type: Literal["created", "updated", "completed", "deleted"]
    task_snapshot: Task  # Full task object at time of event
```

**Alternatives Considered**:
- **Avro Schema Registry (Confluent/Redpanda)**: Rejected - adds external dependency, requires schema registry deployment, overkill for 3 event types
- **Protobuf with Field Numbers**: Rejected - requires protoc compilation step, adds build complexity, harder to debug (binary format)

**Backward Compatibility Rules**:
1. Adding new optional fields: SAFE (consumers ignore unknown fields)
2. Removing fields: BREAKING (bump schema_version, consumers check version)
3. Changing field types: BREAKING (bump schema_version)
4. Renaming fields: BREAKING (bump schema_version)

**Contract Tests**: pytest tests validate schema changes don't break consumers:
```python
def test_task_event_v1_schema_stable():
    """Ensure TaskEvent v1.0 schema hasn't changed."""
    schema = TaskEvent.model_json_schema()
    expected_fields = {"schema_version", "event_type", "task_id", "user_id", "timestamp", "correlation_id", "task_snapshot"}
    assert set(schema["required"]) == expected_fields
```

---

## 2. Dapr Jobs API Best Practices for Reminders

### Decision: Dapr Jobs API with PostgreSQL Actor State Store Persistence

**Rationale**:
- Dapr Jobs API provides exactly-once execution semantics (better than cron polling)
- Jobs persist in actor state store - survive pod restarts, no lost reminders
- Declarative job scheduling via HTTP API - no background job queue infrastructure
- Native integration with Dapr Pub/Sub - job callback publishes to reminders topic

**Implementation**:
```python
# Schedule reminder (in Chat API when task created)
async def schedule_reminder(task: Task, remind_at: datetime):
    job_id = f"reminder-task-{task.id}"
    dapr_jobs_url = f"http://localhost:3500/v1.0-alpha1/jobs/{job_id}"

    await httpx.post(dapr_jobs_url, json={
        "dueTime": remind_at.isoformat() + "Z",  # ISO 8601 UTC
        "data": {
            "task_id": task.id,
            "title": task.title,
            "due_at": task.due_at.isoformat(),
            "user_id": task.user_id
        }
    })

# Job callback endpoint (in Notification Service)
@app.post("/api/jobs/reminder")
async def handle_reminder_job(request: Request):
    job_data = await request.json()

    # Publish to reminders topic via Dapr Pub/Sub
    await dapr_pubsub.publish("kafka-pubsub", "reminders", ReminderEvent(
        task_id=job_data["data"]["task_id"],
        title=job_data["data"]["title"],
        due_at=job_data["data"]["due_at"],
        remind_at=datetime.utcnow(),
        user_id=job_data["data"]["user_id"],
        correlation_id=str(uuid.uuid4())
    ))

    return {"status": "SUCCESS"}
```

**Alternatives Considered**:
- **Cron Job Polling DB**: Rejected - polls every minute wasting cycles, ±1 minute accuracy vs. ±seconds
- **Celery Beat**: Rejected - requires Redis/RabbitMQ broker, adds infrastructure complexity
- **Kubernetes CronJobs**: Rejected - minimum 1 minute granularity, doesn't support dynamic scheduling

**Reliability Considerations**:
- Jobs survive pod restarts (persisted in PostgreSQL via Dapr actor state store)
- If Notification Service crashes, job retries until SUCCESS response
- If job fires but publish fails, Dapr retries (configured: 3 attempts, exponential backoff)
- Idempotency: Notification Service tracks sent reminders in DB to prevent duplicate notifications

**Configuration** (Dapr component):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connection-string
    - name: actorStateStore
      value: "true"  # Enable actor state persistence for Jobs API
```

---

## 3. Kafka Topic Partitioning Strategy

### Decision: Partition by task_id Using murmur2 Hash (Default Kafka Partitioner)

**Rationale**:
- Ordering guarantee: All events for same task go to same partition (e.g., created → updated → completed processed in order)
- Parallel processing: Multiple consumers process different partitions concurrently
- No hotspots: murmur2 hash distributes tasks evenly across partitions
- Simplicity: Default Kafka behavior, no custom partitioner needed

**Implementation**:
```python
# Publish event with task_id as key (Dapr automatically uses key for partitioning)
await httpx.post("http://localhost:3500/v1.0/publish/kafka-pubsub/task-events", json={
    "event_type": "completed",
    "task_id": 123,
    "user_id": "user-456",
    "timestamp": datetime.utcnow().isoformat(),
    "correlation_id": str(uuid.uuid4()),
    "task_snapshot": task.dict()
}, headers={
    "Dapr-Message-Key": str(123)  # Partition by task_id
})
```

**Topic Configuration**:
- **Partitions**: 3 partitions for `task-events` topic (matches 3 consumer replicas for parallel processing)
- **Replication Factor**: 2 (cloud) or 1 (Minikube) - survives single broker failure in cloud
- **Retention**: 90 days (audit log requirement from constitution)

**Alternatives Considered**:
- **Round-robin partitioning**: Rejected - no ordering guarantee, could process completed before created
- **Partition by user_id**: Rejected - creates hotspots if power users generate many tasks
- **Single partition**: Rejected - no parallel processing, bottleneck at scale

**Consumer Group Strategy**:
- Each service (Recurring Tasks, Audit, WebSocket) uses separate consumer group
- Within consumer group, 3 replicas share partitions (each replica processes 1 partition)
- Dapr subscription automatically handles partition assignment and rebalancing

---

## 4. Full-Text Search Implementation

### Decision: PostgreSQL GIN Index on tsvector with to_tsvector('english', ...)

**Rationale**:
- Native PostgreSQL feature - no external search engine (Elasticsearch) deployment
- Sub-second query performance for 10,000 tasks (meets SC-011: <1 second)
- GIN index pre-computes tsvector, avoids runtime text parsing overhead
- Supports ranking by relevance (ts_rank function)

**Implementation**:
```sql
-- Add tsvector column to tasks table
ALTER TABLE tasks ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
    ) STORED;

-- Create GIN index for fast search
CREATE INDEX tasks_search_vector_idx ON tasks USING GIN(search_vector);

-- Query with ranking
SELECT id, title, ts_rank(search_vector, query) AS rank
FROM tasks, to_tsquery('english', 'client & presentation') query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 50;
```

**Performance Characteristics**:
- Index size: ~20% of table size (10k tasks → ~2MB index)
- Query time: 10-50ms for typical 2-3 word queries
- Insert/update overhead: Minimal (<5ms) - tsvector generated automatically

**Alternatives Considered**:
- **Elasticsearch**: Rejected - adds external service, requires synchronization between PostgreSQL and Elasticsearch, overkill for 10k documents
- **PostgreSQL LIKE queries**: Rejected - full table scan, slow for >1000 tasks
- **Trigram indexes (pg_trgm)**: Considered - good for typo tolerance, but GIN + tsvector better for multi-word queries with boolean logic

**Search Query Features**:
- Boolean operators: "client & presentation" (AND), "client | presentation" (OR), "client & !presentation" (NOT)
- Phrase search: "'weekly team meeting'" (exact phrase)
- Prefix search: "presen:*" (matches presentation, present, presenter)
- Ranking: Results sorted by relevance score (ts_rank)

**Fallback for Non-English**:
- Use 'simple' dictionary instead of 'english' for non-English text (disables stemming)
- Future enhancement: Detect user language and use appropriate dictionary

---

## 5. Recurring Task Calculation

### Decision: python-dateutil's rrule (RFC 5545 iCalendar Standard)

**Rationale**:
- Battle-tested library (used in Google Calendar, Outlook, Mozilla)
- Handles edge cases: leap years, DST transitions, month-end dates (Jan 31 → Feb 28)
- Supports all required patterns: daily, weekly (multiple days), monthly (date or last day)
- Pythonic API with clear recurrence rule syntax

**Installation**:
```bash
pip install python-dateutil
```

**Implementation**:
```python
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from datetime import datetime

# Daily recurrence
def calculate_next_daily(completed_at: datetime, interval: int = 1) -> datetime:
    """Calculate next instance for daily recurrence."""
    rule = rrule(DAILY, interval=interval, count=1, dtstart=completed_at)
    return list(rule)[0]

# Weekly recurrence (specific days of week)
def calculate_next_weekly(completed_at: datetime, days_of_week: list[int]) -> datetime:
    """Calculate next instance for weekly recurrence.

    days_of_week: [0=Mon, 1=Tue, ..., 6=Sun]
    """
    rule = rrule(WEEKLY, byweekday=days_of_week, count=1, dtstart=completed_at)
    return list(rule)[0]

# Monthly recurrence (same day of month)
def calculate_next_monthly(completed_at: datetime, day_of_month: int) -> datetime:
    """Calculate next instance for monthly recurrence on specific date.

    day_of_month: 1-31, or -1 for last day of month
    """
    if day_of_month == -1:
        rule = rrule(MONTHLY, bymonthday=-1, count=1, dtstart=completed_at)
    else:
        rule = rrule(MONTHLY, bymonthday=day_of_month, count=1, dtstart=completed_at)
    return list(rule)[0]
```

**Edge Case Handling**:
- Monthly on Jan 31 → Feb 28/29 (non-leap/leap year) → Mar 31
- Weekly on Monday → Next Monday (7 days later), not same day
- DST transitions: rrule handles automatically, preserves local time

**Alternatives Considered**:
- **Manual date math (timedelta)**: Rejected - brittle, doesn't handle month boundaries, leap years, DST
- **APScheduler's CronTrigger**: Rejected - cron syntax less intuitive than rrule for recurrence patterns
- **Custom recurrence engine**: Rejected - reinventing wheel, high bug risk for date edge cases

**Testing Strategy**:
- Unit tests for all edge cases: leap years, DST, month-end rollover, weekly multiple days
- Property-based testing (Hypothesis) to generate random recurrence patterns and verify consistency

---

## 6. Dapr Component Configuration Best Practices

### Decision: Retry Policy (3x, Exponential Backoff) + Circuit Breaker (5 Failures → 30s Break)

**Rationale**:
- Transient failures (network glitches, temporary broker unavailability) handled automatically
- Circuit breaker prevents cascading failures (if Kafka down, stop trying after 5 failures)
- Exponential backoff reduces load on failing systems during recovery
- Aligns with constitution requirement: "Services MUST handle partial failures gracefully"

**Dapr Configuration**:

```yaml
# Pub/Sub Component with Retry + Circuit Breaker
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "taskflow-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: authRequired
      value: "false"  # For local Kafka; use SASL_SSL in cloud
    # Retry configuration
    - name: maxRetries
      value: "3"
    - name: retryBackOff
      value: "exponential"  # 1s, 2s, 4s delays
    # Circuit breaker configuration
    - name: circuitBreakerThreshold
      value: "5"  # Open circuit after 5 consecutive failures
    - name: circuitBreakerTimeout
      value: "30s"  # Half-open after 30 seconds

# State Store Component
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connection-string
    - name: maxIdleConns
      value: "10"  # Connection pool size
    - name: maxOpenConns
      value: "50"
    - name: connMaxLifetime
      value: "3600s"  # 1 hour connection lifetime
    - name: actorStateStore
      value: "true"  # Enable for Dapr Jobs API
```

**Service-Level Timeout Configuration**:
```python
# In application code (Chat API)
async def publish_event(topic: str, event: dict, timeout: float = 5.0):
    """Publish event with timeout to prevent indefinite blocking."""
    try:
        response = await httpx.post(
            f"http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}",
            json=event,
            timeout=timeout  # 5 second timeout
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(f"Timeout publishing to {topic}", extra={"event": event})
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error publishing to {topic}: {e.response.status_code}")
        raise
```

**Monitoring Alerts**:
- Circuit breaker open: Alert on-call when circuit trips (indicates sustained Kafka outage)
- Retry exhaustion: Alert on Prometheus metric `dapr_component_retries_exhausted_total` >10/min

**Alternatives Considered**:
- **No retries**: Rejected - requires manual intervention for transient failures
- **Infinite retries**: Rejected - could block application forever during sustained outage
- **Fixed backoff**: Rejected - exponential backoff better for recovering systems (gives them time to stabilize)

---

## 7. Zero-Downtime Deployment Strategy

### Decision: Helm Rolling Updates + PodDisruptionBudget + Readiness Gates

**Rationale**:
- Rolling update ensures old pods serve traffic until new pods ready
- PodDisruptionBudget prevents simultaneous termination of multiple pods
- Readiness gates delay traffic routing until health checks pass
- Aligns with constitution SC-015: "Zero-downtime deployments achieve 100% success rate"

**Helm Chart Configuration**:

```yaml
# values.yaml (Chat API deployment)
chatApi:
  replicaCount: 3  # Minimum 2 for zero-downtime
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1  # Keep 2/3 pods available during update
      maxSurge: 1  # Spin up 1 extra pod before terminating old

  podDisruptionBudget:
    enabled: true
    minAvailable: 2  # Always keep 2 pods available

  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 1
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /ready
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 1
    successThreshold: 1  # Pod ready after 1 successful check
    failureThreshold: 3

  lifecycle:
    preStop:
      exec:
        command: ["/bin/sh", "-c", "sleep 15"]  # Graceful shutdown: wait 15s for in-flight requests
```

**Deployment Process**:
```bash
# 1. Dry-run to validate changes
helm upgrade --install todo-app k8s/helm-charts/todo-app/ --dry-run --debug

# 2. Deploy with rollback on failure
helm upgrade --install todo-app k8s/helm-charts/todo-app/ --wait --timeout 10m --atomic

# --wait: Wait for all pods to be ready
# --timeout: Fail if not ready in 10 minutes
# --atomic: Rollback on failure
```

**Validation Tests** (part of CI/CD pipeline):
- Smoke test during deployment: Curl /health endpoint, expect 200 OK from both old and new pods
- Load test during deployment: Generate traffic, verify 0 errors, <200ms latency maintained
- Rollback test: Introduce failing health check, verify Helm automatically rolls back

**Alternatives Considered**:
- **Blue-Green Deployment**: Rejected - requires 2x infrastructure capacity, wasteful for single-tenant
- **Canary Deployment**: Considered for future - incrementally route traffic (5% → 50% → 100%), more complex than rolling update
- **Recreate Strategy**: Rejected - causes downtime (terminates all pods before creating new ones)

**Database Migration Coordination**:
- Migrations run as Helm pre-upgrade hook (Job that completes before new pods start)
- Migrations MUST be backward-compatible (old app version works with new schema)
- Example: Add optional column with NULL default, then deploy new app that populates it

---

## 8. Distributed Tracing Sampling Strategy

### Decision: 10% Sampling for Production, 100% for Development/Staging

**Rationale**:
- 100% tracing in production generates excessive data (1000 req/sec → 1000 traces/sec → storage overload)
- 10% sampling captures sufficient data for debugging (100 traces/sec → 6000/min → trends visible)
- Tail-based sampling: Always trace slow requests (>1s) and errors, even if outside 10% sample
- Development/staging: 100% sampling for complete visibility during testing

**Dapr Configuration**:

```yaml
# Dapr configuration (applied at cluster level)
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing-config
spec:
  tracing:
    samplingRate: "0.1"  # 10% sampling (override with env var for dev)
    zipkin:
      endpointAddress: "http://zipkin.monitoring.svc.cluster.local:9411/api/v2/spans"

---
# Override sampling for development namespace
apiVersion: v1
kind: ConfigMap
metadata:
  name: dapr-config
  namespace: development
data:
  config.yaml: |
    spec:
      tracing:
        samplingRate: "1.0"  # 100% for dev/staging
```

**Application-Level Trace Enrichment**:
```python
# Add custom span attributes for better debugging
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("task_create") as span:
    span.set_attribute("task.id", task.id)
    span.set_attribute("task.priority", task.priority)
    span.set_attribute("user.id", task.user_id)

    # Business logic
    await task_service.create(task)
```

**Zipkin Deployment** (in monitoring namespace):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zipkin
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zipkin
  template:
    metadata:
      labels:
        app: zipkin
    spec:
      containers:
      - name: zipkin
        image: openzipkin/zipkin:latest
        ports:
        - containerPort: 9411
        env:
        - name: STORAGE_TYPE
          value: "mem"  # In-memory for dev; use Elasticsearch for prod
```

**Trace Retention**:
- Development: 7 days (sufficient for debugging recent issues)
- Production: 30 days (for trend analysis and incident investigation)

**Alternatives Considered**:
- **100% tracing in production**: Rejected - excessive storage cost (50GB/day traces), impacts performance
- **Head-based sampling (random 10%)**: Rejected - could miss critical slow/error traces
- **Tail-based sampling only**: Considered for future - requires aggregator service (Jaeger, Grafana Tempo)

---

## 9. Event Dead Letter Queue (DLQ) Pattern

### Decision: Dapr + Kafka DLQ with Max 3 Retries, Prometheus Alert on DLQ Depth >10

**Rationale**:
- Failed event processing (e.g., consumer bug, invalid event format) shouldn't block entire queue
- DLQ isolates poison messages while allowing healthy events to process
- Prometheus alert enables proactive response to processing failures
- Aligns with constitution reliability standards: "Retry Policy: Failed event processing retried up to 3 times"

**Dapr Subscription Configuration** (with DLQ):

```yaml
# Dapr subscription for Recurring Task Service
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  route: /events/task-completed
  metadata:
    # Retry configuration
    maxRetries: "3"
    retryPattern: "exponential"  # 1s, 2s, 4s
    # Dead letter queue
    deadLetterTopic: "task-events-dlq"
```

**DLQ Consumer** (monitoring/alerting service):
```python
# Monitor DLQ depth and alert
@app.post("/events/dlq")
async def handle_dlq_event(request: Request):
    """Handle events that failed processing after 3 retries."""
    event = await request.json()

    # Log detailed error for investigation
    logger.error("Event processing failed after retries", extra={
        "event": event,
        "topic": event.get("topic"),
        "error": event.get("error")
    })

    # Increment DLQ metric for alerting
    dlq_depth_gauge.labels(topic="task-events").inc()

    # Future enhancement: Send to incident response system (PagerDuty, Opsgenie)

    return {"status": "logged"}
```

**Prometheus Alert Rule**:
```yaml
groups:
- name: event_processing
  rules:
  - alert: DLQDepthHigh
    expr: dlq_depth{topic="task-events"} > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High DLQ depth for task-events topic"
      description: "{{ $value }} events in DLQ - indicates processing failures"
```

**DLQ Investigation Workflow**:
1. Alert fires → On-call engineer investigates Zipkin traces for failed events
2. Identify root cause (bug in consumer, invalid event format, external dependency failure)
3. Fix bug, deploy new consumer version
4. Replay DLQ events manually: Publish from DLQ topic back to main topic after fix

**Alternatives Considered**:
- **No DLQ**: Rejected - poison message blocks entire partition, impacts all consumers
- **Infinite retries**: Rejected - could retry forever on permanent failure (e.g., schema mismatch)
- **Manual DLQ processing**: Rejected - prefer automated alerting for proactive response

---

## 10. Kubernetes Autoscaling for Event-Driven Workloads

### Decision: HPA on Custom Metric (Kafka Consumer Lag >100 Messages)

**Rationale**:
- CPU/memory autoscaling insufficient for event-driven workloads (consumer might be idle with low CPU but have backlog)
- Kafka consumer lag is direct indicator of processing capacity (lag >100 → scale up)
- Prevents reminder delays during traffic spikes (e.g., 100 users create tasks with due dates simultaneously)
- Aligns with constitution performance goals: "Event consumer lag stays below 5 seconds during normal operation"

**Prometheus Kafka Exporter** (collects consumer lag metrics):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-exporter
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka-exporter
  template:
    metadata:
      labels:
        app: kafka-exporter
    spec:
      containers:
      - name: kafka-exporter
        image: danielqsj/kafka-exporter:latest
        args:
        - --kafka.server=taskflow-kafka-bootstrap.kafka.svc.cluster.local:9092
        ports:
        - containerPort: 9308
```

**HPA Configuration** (for Recurring Task Service):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recurring-tasks-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recurring-tasks
  minReplicas: 2
  maxReplicas: 10
  metrics:
  # Scale on consumer lag (primary metric)
  - type: Pods
    pods:
      metric:
        name: kafka_consumer_lag
      target:
        type: AverageValue
        averageValue: "100"  # Scale up if lag >100 messages per pod
  # Scale on CPU (secondary metric, catch-all)
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down (prevent flapping)
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately on lag spike
      policies:
      - type: Pods
        value: 2  # Add 2 pods at a time
        periodSeconds: 60
```

**Custom Metrics Adapter** (exposes Kafka lag to HPA):

```bash
# Install Prometheus Adapter for custom metrics
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --set prometheus.url=http://prometheus.monitoring.svc.cluster.local \
  --set rules.custom[0].seriesQuery='kafka_consumer_lag' \
  --set rules.custom[0].metricsQuery='sum(kafka_consumer_lag{topic="task-events",group="recurring-tasks"})' \
  --set rules.custom[0].name.as='kafka_consumer_lag' \
  --set rules.custom[0].namespace.namespaceName='default'
```

**Testing Autoscaling**:
```bash
# Generate load: Publish 1000 task completion events
for i in {1..1000}; do
  curl -X POST http://chat-api/tasks/${i}/complete
done

# Verify HPA scales up
kubectl get hpa recurring-tasks-hpa --watch
# Expected: currentReplicas increases from 2 → 4 → 6 as lag grows

# Verify scale-down after load stops
# Expected: After 5 min stabilization, scales back to 2 replicas
```

**Alternatives Considered**:
- **CPU-based autoscaling only**: Rejected - consumer idle but backlog growing (lag ignored)
- **Fixed replica count**: Rejected - wastes resources during low traffic, insufficient during spikes
- **KEDA (Kubernetes Event-Driven Autoscaling)**: Considered for future - built-in Kafka scaler, simpler than Prometheus adapter, but adds external dependency

---

## Summary of Technology Stack

**Backend Services**:
- Language: Python 3.11
- Framework: FastAPI 0.104+ (async REST API)
- Database ORM: SQLModel (Pydantic + SQLAlchemy)
- HTTP Client: httpx (for Dapr API calls)
- Recurrence: python-dateutil (rrule)
- Testing: pytest, pytest-asyncio, Hypothesis

**Frontend**:
- Framework: Next.js 14 (React, App Router)
- State Management: TanStack Query (server state), Zustand (client state)
- Styling: Tailwind CSS
- Testing: Playwright (E2E)

**Infrastructure**:
- Container Orchestration: Kubernetes 1.28+
- Package Manager: Helm 3.13+
- Service Mesh: Dapr 1.12+ (sidecar pattern)
- Event Streaming: Kafka (Strimzi operator) or Redpanda Cloud
- Database: Neon Serverless PostgreSQL
- Monitoring: Prometheus + Grafana
- Tracing: Zipkin
- Logs: Fluent Bit → Loki

**Cloud Platforms** (pick one):
- Oracle Cloud (OKE) - Recommended: Always free tier, 4 OCPUs, 24GB RAM
- Azure (AKS) - $200 credits, 30 days
- Google Cloud (GKE) - $300 credits, 90 days

**CI/CD**:
- GitHub Actions (free for public repos)
- Docker Hub or GitHub Container Registry (image storage)

---

## Next Steps

1. **Phase 1**: Use research findings to generate data-model.md, contracts/, and quickstart.md
2. **ADR Creation**: Document key decisions as ADRs:
   - Event Schema Versioning Strategy (JSON Schema with version field)
   - Kafka Partitioning Strategy (partition by task_id)
   - Autoscaling Strategy (HPA on consumer lag)
3. **Implementation**: Follow Agentic Dev Stack workflow with research-backed technology choices
4. **Validation**: Test all decisions in Minikube before cloud deployment

**Research Status**: ✅ COMPLETE - All 10 technology decisions resolved with rationale, implementation details, and alternatives considered
