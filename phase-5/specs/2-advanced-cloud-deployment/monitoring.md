# Monitoring and Observability Guide

This guide covers the monitoring, logging, and tracing infrastructure for the Todo App microservices.

## Overview

The monitoring stack consists of:
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **Zipkin**: Distributed tracing
- **Loki** (optional): Log aggregation
- **AlertManager**: Alert routing and silencing

## Quick Start

### Deploy Monitoring Stack

```bash
cd k8s/monitoring

# Deploy all monitoring components
./deploy-monitoring.sh

# Or deploy manually with Helm
helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --values prometheus/prometheus-values.yaml
```

### Access Dashboards

```bash
# Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# http://localhost:3000 (admin/admin)

# Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# http://localhost:9090

# Zipkin
kubectl port-forward -n monitoring svc/zipkin 9411:9411
# http://localhost:9411
```

## Metrics

### Application Metrics

Each service exposes metrics at `/metrics` endpoint:

```python
# Example metrics in services
from prometheus_client import Counter, Histogram, Gauge

# Request counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Active connections
active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)
```

### Custom Business Metrics

```python
# Task operations
tasks_created_total = Counter('tasks_created_total', 'Total tasks created')
tasks_completed_total = Counter('tasks_completed_total', 'Total tasks completed')
recurring_tasks_generated_total = Counter('recurring_tasks_generated_total', 'Recurring tasks generated')

# Event processing
events_published_total = Counter(
    'events_published_total',
    'Total events published',
    ['topic', 'event_type']
)

events_processed_total = Counter(
    'events_processed_total',
    'Total events processed',
    ['topic', 'event_type', 'result']
)

event_processing_duration_seconds = Histogram(
    'event_processing_duration_seconds',
    'Event processing duration',
    ['topic', 'event_type']
)

# Reminders
reminders_scheduled_total = Counter('reminders_scheduled_total', 'Total reminders scheduled')
reminders_sent_total = Counter(
    'reminders_sent_total',
    'Total reminders sent',
    ['channel', 'status']
)
```

### Dapr Metrics

Dapr automatically exposes metrics:
- `dapr_http_server_request_count`
- `dapr_http_server_request_duration_ms`
- `dapr_component_pubsub_ingress_total`
- `dapr_component_pubsub_egress_total`
- `dapr_runtime_service_invocation_req_sent_total`

## Alerts

### Service Health Alerts

**ServiceDown**
- Condition: Service is unreachable for 2+ minutes
- Severity: Critical
- Action: Check pod status, logs, and recent deployments

**HighErrorRate**
- Condition: Error rate > 5% for 5 minutes
- Severity: Warning
- Action: Check logs for error details, review recent changes

**HighLatency**
- Condition: p95 latency > 1s for 5 minutes
- Severity: Warning
- Action: Check database queries, external API calls, resource usage

### Resource Alerts

**HighMemoryUsage**
- Condition: Memory usage > 85% for 5 minutes
- Severity: Warning
- Action: Check for memory leaks, increase limits if needed

**HighCPUUsage**
- Condition: CPU usage > 85% for 5 minutes
- Severity: Warning
- Action: Check for CPU-intensive operations, scale horizontally

**PodRestartingTooOften**
- Condition: Pod restarts > 0.1/minute for 15 minutes
- Severity: Warning
- Action: Check crash logs, review health check configuration

### Event Processing Alerts

**HighEventProcessingFailures**
- Condition: Event processing failure rate > 5% for 5 minutes
- Severity: Critical
- Action: Check consumer logs, verify Kafka connectivity, check message format

**KafkaConsumerLag**
- Condition: Consumer lag > 1000 messages for 5 minutes
- Severity: Warning
- Action: Scale consumers, check processing speed, verify no blocking operations

## Dashboards

### Todo App Overview Dashboard

Provides high-level metrics:
- Services Up/Down status
- Request rate per service
- Error rate per service
- Latency percentiles (p50, p95, p99)
- CPU and memory usage

### Event Processing Dashboard

Tracks event-driven architecture:
- Events published per topic
- Events processed per topic
- Event processing duration
- Event processing failures
- Kafka consumer lag
- Dapr Pub/Sub metrics

### Database Dashboard

Monitors database performance:
- Query duration (p50, p95, p99)
- Connection pool usage
- Slow queries
- Transaction rate
- Database size

## Distributed Tracing

### Enable Tracing in Services

Dapr automatically injects trace context. To add custom spans:

```python
from opentelemetry import trace
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure Zipkin exporter
zipkin_exporter = ZipkinExporter(
    endpoint="http://zipkin.monitoring.svc.cluster.local:9411/api/v2/spans"
)

# Setup tracer
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(zipkin_exporter)
)

tracer = trace.get_tracer(__name__)

# Add custom spans
@app.post("/tasks")
async def create_task(task: TaskCreate):
    with tracer.start_as_current_span("create_task") as span:
        span.set_attribute("task.title", task.title)
        # ... task creation logic
```

### Viewing Traces

1. Access Zipkin UI: `http://localhost:9411`
2. Select service (e.g., chat-api)
3. Find traces by:
   - Service name
   - Operation name
   - Tags (e.g., error=true)
   - Duration

## Logging

### Structured Logging

All services use structured JSON logging:

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "task_created",
    task_id=task.id,
    user_id=user.id,
    correlation_id=correlation_id
)

logger.error(
    "event_processing_failed",
    topic="task-events",
    error=str(e),
    correlation_id=correlation_id
)
```

### Log Aggregation with Loki (Optional)

```bash
# Install Loki
helm install loki grafana/loki-stack \
    --namespace monitoring \
    --set grafana.enabled=false

# Configure Grafana datasource
# Add Loki datasource: http://loki:3100
```

### Viewing Logs

```bash
# View logs for a service
kubectl logs -f deployment/todo-app-chat-api -n todo-app -c chat-api

# View Dapr sidecar logs
kubectl logs -f deployment/todo-app-chat-api -n todo-app -c daprd

# Logs with correlation ID
kubectl logs deployment/todo-app-chat-api -n todo-app | grep "correlation_id=abc123"

# Logs with Loki (via Grafana)
# Query: {app="chat-api"} |= "error"
```

## Performance Monitoring

### Key Performance Indicators (KPIs)

**Service Level Indicators (SLIs)**:
- Availability: 99.9% uptime
- Latency: p95 < 200ms for API requests
- Error Rate: < 1% of requests
- Event Processing: < 5s end-to-end latency

**Service Level Objectives (SLOs)**:
- 99.9% of requests complete in < 200ms
- 99.99% of events processed successfully
- Zero data loss for persistent storage

### Monitoring Queries

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# p95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# CPU usage percentage
rate(container_cpu_usage_seconds_total[5m]) / container_spec_cpu_quota * 100000 * 100

# Memory usage percentage
container_memory_working_set_bytes / container_spec_memory_limit_bytes * 100

# Event processing rate
rate(events_processed_total[5m])

# Kafka consumer lag
kafka_consumer_group_lag
```

## Troubleshooting

### High Latency

1. Check database query performance
2. Review external API call duration
3. Check for N+1 queries
4. Verify connection pool settings
5. Check resource constraints (CPU/memory)

### High Error Rate

1. Check application logs for error details
2. Verify database connectivity
3. Check Kafka broker health
4. Review recent deployments
5. Check for configuration errors

### Memory Leaks

1. Check memory usage trends over time
2. Profile application with memory profiler
3. Review object lifecycle management
4. Check for unclosed connections
5. Monitor garbage collection

### Event Processing Issues

1. Check Kafka broker connectivity
2. Verify consumer group status
3. Check event schema compatibility
4. Review dead letter queue
5. Verify Dapr component configuration

## Best Practices

1. **Always include correlation IDs** for request tracing
2. **Log at appropriate levels**: DEBUG, INFO, WARNING, ERROR
3. **Include context in log messages**: user_id, task_id, etc.
4. **Monitor business metrics** in addition to technical metrics
5. **Set up alerts for critical issues** with appropriate thresholds
6. **Review dashboards regularly** to identify trends
7. **Test alert rules** to avoid alert fatigue
8. **Document runbooks** for common issues

## Resources

- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Zipkin Documentation](https://zipkin.io/pages/quickstart)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Dapr Observability](https://docs.dapr.io/operations/observability/)
