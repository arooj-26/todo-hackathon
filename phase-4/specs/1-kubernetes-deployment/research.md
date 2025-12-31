# Research: Technology Decisions for Kubernetes Deployment

**Feature**: Kubernetes Deployment for Todo Chatbot
**Date**: 2025-12-30
**Status**: Complete

This document captures research findings and technology decisions made during the planning phase of the Kubernetes deployment feature.

---

## 1. Docker Base Images

### Decision: python:3.11-slim for Backend, node:18-alpine for Frontend

**Options Considered**:
1. **python:3.11-slim** (Debian-based, minimal)
2. **python:3.11-alpine** (Alpine Linux-based, smaller)
3. **node:18-alpine** (Alpine Linux-based, minimal)
4. **node:18-slim** (Debian-based, minimal)

**Rationale**:
- **python:3.11-slim chosen over alpine**:
  - Faster builds: No need to compile C extensions (psycopg2, bcrypt)
  - Better compatibility: Debian-based matches local development
  - Acceptable size: ~150MB vs ~50MB alpine (worth it for build speed)
  - Production-ready: Standard choice for FastAPI applications

- **node:18-alpine chosen for frontends**:
  - Smallest size: ~110MB vs ~200MB for node:18-slim
  - Fast builds: No heavy compilation required for Next.js
  - Security: Smaller attack surface, fewer packages
  - Standard practice: Alpine commonly used for Node.js frontends

**Alternatives Considered**:
- **scratch** or **distroless** images rejected: Too complex for development, debugging difficult
- **Full Debian** images rejected: Unnecessarily large (500MB+)

**Implementation**:
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim as builder
# ... build stage ...

FROM python:3.11-slim as runtime
# ... runtime stage ...

# Frontend Dockerfile
FROM node:18-alpine as builder
# ... build stage ...

FROM node:18-alpine as runtime
# ... runtime stage ...
```

---

## 2. Multi-Stage Docker Builds

### Decision: Use Multi-Stage Builds for All Images

**Options Considered**:
1. **Single-stage builds** (simple, larger images)
2. **Multi-stage builds** (complex, optimized images)
3. **External build tools** (BuildKit, Kaniko)

**Rationale**:
- **Multi-stage builds selected**:
  - Smaller final images: Build dependencies excluded from runtime
  - Security: Fewer tools and packages in production image
  - Caching: Build stage cached separately from runtime
  - Standard practice: Recommended by Docker and Kubernetes community

**Build Stage Pattern**:
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
COPY app/ ./app/
```

**Runtime Stage Pattern**:
```dockerfile
FROM python:3.11-slim as runtime
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app/ ./app/
ENV PATH=/root/.local/bin:$PATH
USER python
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Alternatives Considered**:
- **Single-stage rejected**: Images 2-3x larger, includes build tools
- **External tools rejected**: Adds complexity, not needed for local development

---

## 3. Helm Chart Structure

### Decision: Single Helm Chart for Entire Application

**Options Considered**:
1. **Single chart** with all services (simple, monolithic)
2. **Multiple charts** (one per service)
3. **Umbrella chart** with subcharts
4. **Helm dependencies** (Chart.yaml dependencies)

**Rationale**:
- **Single chart selected**:
  - Simplicity: All resources deployed together
  - Consistency: Single version number for entire application
  - Atomic deployments: All services update simultaneously
  - Easier testing: Single `helm install` command
  - Aligned with constitution**: Principle VII (Simplicity and Pragmatism)

**Chart Structure**:
```
todo-app/
├── Chart.yaml           # Metadata: name, version, description
├── values.yaml          # Configuration values
├── .helmignore          # Ignore patterns
├── README.md            # Chart documentation
└── templates/           # Kubernetes resource templates
    ├── _helpers.tpl     # Template helpers
    ├── configmap.yaml   # Non-sensitive config
    ├── secrets.yaml     # Sensitive data
    ├── *-deployment.yaml # Deployments (5 total)
    └── *-service.yaml   # Services (5 total)
```

**Alternatives Considered**:
- **Multiple charts rejected**: Over-engineering for 5 services, harder to manage
- **Umbrella chart rejected**: Adds complexity without clear benefit for local deployment

---

## 4. Kubernetes Service Types

### Decision: NodePort for Frontends, ClusterIP for Backends/Database

**Options Considered**:
1. **NodePort** (external access via node IP + port)
2. **ClusterIP** (internal-only, default)
3. **LoadBalancer** (cloud provider integration)
4. **Ingress** (HTTP routing, requires controller)

**Rationale**:
- **NodePort for frontends**:
  - Direct browser access: `http://<minikube-ip>:30000`
  - No Ingress controller needed: Simpler setup
  - Fixed ports: 30000 (Todo), 30001 (Chatbot)
  - Development-friendly: Easy to access locally

- **ClusterIP for backends/database**:
  - Internal-only: Not accessible from outside cluster
  - Service discovery: Kubernetes DNS (e.g., `todo-backend:8000`)
  - Security: Reduces attack surface
  - Standard practice: Frontends call backends via ClusterIP

**Service Type Matrix**:
| Service | Type | Port | NodePort | Access |
|---------|------|------|----------|--------|
| todo-frontend | NodePort | 3000 | 30000 | Browser |
| todo-backend | ClusterIP | 8000 | N/A | Internal |
| chatbot-frontend | NodePort | 3001 | 30001 | Browser |
| chatbot-backend | ClusterIP | 8001 | N/A | Internal |
| postgresql | ClusterIP | 5432 | N/A | Internal |

**Alternatives Considered**:
- **LoadBalancer rejected**: Requires cloud provider, not available in Minikube
- **Ingress rejected**: Adds complexity (controller, TLS), not needed for local access

---

## 5. Health Probe Configuration

### Decision: HTTP Probes for All Services

**Options Considered**:
1. **HTTP probes** (GET request to /health)
2. **Exec probes** (run command in container)
3. **TCP probes** (check port open)
4. **No probes** (rely on process monitoring)

**Rationale**:
- **HTTP probes selected**:
  - Application-level health: Checks if app is responsive
  - Readiness vs liveness: Different endpoints for different purposes
  - Standard practice: FastAPI and Next.js both support HTTP health checks
  - Debugging-friendly: Can test health endpoint manually with `curl`

**Probe Configuration Pattern**:
```yaml
livenessProbe:
  httpGet:
    path: /health        # or / for Next.js
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready         # or /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

**Probe Purposes**:
- **Liveness**: Is the container alive? (If fails → restart container)
- **Readiness**: Is the container ready to serve traffic? (If fails → remove from service endpoints)

**Alternatives Considered**:
- **Exec probes rejected**: Slower, harder to debug, requires shell in container
- **TCP probes rejected**: Only checks port open, not application health
- **No probes rejected**: Violates constitution Principle VI (Observability)

---

## 6. Resource Limits and Requests

### Decision: Conservative Limits with Room for Growth

**Options Considered**:
1. **No limits** (unlimited resources, risky)
2. **Tight limits** (minimal resources, may throttle)
3. **Conservative limits** (balanced approach)
4. **Burstable** (requests < limits for spikes)

**Rationale**:
- **Conservative limits selected**:
  - Prevents resource exhaustion: One pod can't consume all cluster resources
  - Room for growth: Limits higher than typical usage
  - Minikube constraints: Total 4 CPU, 8GB RAM available
  - Testing-friendly: Not so tight that normal usage triggers throttling

**Resource Allocation**:
| Service | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit | Total CPU | Total Memory |
|---------|----------|-------------|-----------|----------------|--------------|-----------|--------------|
| todo-frontend | 2 | 200m | 500m | 256Mi | 512Mi | 1000m | 1024Mi |
| todo-backend | 1 | 250m | 500m | 256Mi | 512Mi | 500m | 512Mi |
| chatbot-frontend | 2 | 200m | 500m | 256Mi | 512Mi | 1000m | 1024Mi |
| chatbot-backend | 1 | 250m | 500m | 256Mi | 512Mi | 500m | 512Mi |
| postgresql | 1 | 250m | 500m | 512Mi | 1024Mi | 500m | 1024Mi |
| **TOTAL** | **7 pods** | - | - | - | - | **3500m** | **4096Mi** |

**Buffer**: ~15% CPU, ~50% memory remaining for system pods and spikes

**Alternatives Considered**:
- **No limits rejected**: Risk of OOM kills, cluster instability
- **Tight limits rejected**: May cause throttling during normal usage

---

## 7. Environment Variable Management

### Decision: ConfigMap for Non-Sensitive, Secrets for Sensitive

**Options Considered**:
1. **ConfigMap only** (simple, insecure)
2. **Secrets only** (secure, verbose)
3. **ConfigMap + Secrets** (balanced)
4. **External secret managers** (Vault, AWS Secrets Manager)

**Rationale**:
- **ConfigMap + Secrets selected**:
  - Clear separation: Config vs credentials
  - Security: Secrets base64-encoded (minimal), not in Git
  - Helm templating: Both support `{{ .Values.* }}` syntax
  - Kubernetes-native: No external dependencies
  - Constitution compliance: Principle V (Security by Default)

**ConfigMap (Non-Sensitive)**:
- Database host (`postgresql:5432`)
- Service URLs (`http://todo-backend:8000`)
- Port numbers (3000, 8000, etc.)
- Environment flags (`ENVIRONMENT=development`)

**Secret (Sensitive)**:
- Database password (`POSTGRES_PASSWORD`)
- JWT secret key (`SECRET_KEY`)
- OpenAI API key (`OPENAI_API_KEY`)

**Implementation Pattern**:
```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_HOST: "postgresql"
  TODO_API_URL: "http://todo-backend:8000"

# Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  POSTGRES_PASSWORD: {{ .Values.secrets.postgresPassword | b64enc }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | b64enc }}
```

**Alternatives Considered**:
- **ConfigMap only rejected**: Violates security principle
- **External secret managers rejected**: Over-engineering for local development

---

## 8. PostgreSQL Storage

### Decision: PersistentVolumeClaim with 5Gi Size

**Options Considered**:
1. **EmptyDir** (ephemeral, lost on pod restart)
2. **HostPath** (local directory, node-dependent)
3. **PersistentVolumeClaim** (persistent, node-independent)
4. **External database** (managed service)

**Rationale**:
- **PersistentVolumeClaim selected**:
  - Data persistence: Survives pod restarts and deletions
  - Node-independent: Can move to different node
  - Kubernetes-native: Standard storage abstraction
  - Testing-friendly: Can test pod restart without data loss

**PVC Configuration**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce      # Single node access (PostgreSQL is single instance)
  resources:
    requests:
      storage: 5Gi       # Sufficient for development (tasks, conversations)
  storageClassName: standard  # Minikube default storage class
```

**Storage Requirements**:
- **Development**: 5Gi sufficient (tasks, conversations, users)
- **Production** (future): Managed database (Neon, AWS RDS)

**Alternatives Considered**:
- **EmptyDir rejected**: Data loss on pod restart violates FR-030
- **HostPath rejected**: Node-dependent, not portable
- **External database rejected**: Out of scope for Phase IV (local deployment)

---

## 9. Image Pull Policy

### Decision: Never (Use Local Minikube Images)

**Options Considered**:
1. **Always** (pull from registry every time)
2. **IfNotPresent** (pull if not cached)
3. **Never** (use local images only)

**Rationale**:
- **Never selected**:
  - No external registry: Images built locally in Minikube
  - Faster deployments: No pull time
  - Offline-friendly: Works without internet
  - Development workflow: Build locally, test immediately
  - Avoids ImagePullBackOff: Common error when Minikube can't reach registry

**Implementation**:
```yaml
spec:
  containers:
    - name: todo-backend
      image: todo-backend:v1
      imagePullPolicy: Never  # Use local Minikube image
```

**Workflow**:
1. Point Docker to Minikube: `eval $(minikube docker-env)`
2. Build images: `docker build -t todo-backend:v1 .`
3. Deploy: `helm install todo-app ./todo-app` (uses local images)

**Alternatives Considered**:
- **Always/IfNotPresent rejected**: Requires external registry (DockerHub, ECR), adds complexity

---

## 10. kubectl-ai Usage Patterns

### Decision: Use for Operations, Not Chart Generation

**Options Considered**:
1. **kubectl-ai for chart generation** (AI generates YAML)
2. **kubectl-ai for operations only** (deploy, monitor, debug)
3. **kubectl-ai not used** (standard kubectl only)

**Rationale**:
- **kubectl-ai for operations selected**:
  - Chart generation: Claude Code better suited (comprehensive, templated, validated)
  - Operations strength: kubectl-ai excels at natural language operations
  - Debugging: Fast troubleshooting with "why is pod failing?"
  - Monitoring: Quick status checks without memorizing kubectl syntax
  - Constitution compliance: Principle III (AI-Assisted DevOps)

**kubectl-ai Best Practices**:
| Task | kubectl-ai Command | Traditional kubectl |
|------|-------------------|---------------------|
| Check status | `kubectl-ai "show all pods"` | `kubectl get pods` |
| Debug failure | `kubectl-ai "why is pod crashing?"` | `kubectl describe pod <name> && kubectl logs <name>` |
| Scale deployment | `kubectl-ai "scale todo-backend to 3"` | `kubectl scale deployment todo-backend --replicas=3` |
| Get service URLs | `kubectl-ai "how do I access frontends?"` | `minikube service todo-frontend --url` |

**Alternatives Considered**:
- **kubectl-ai for chart generation rejected**: Instructions clarify Claude Code is better tool
- **Not using kubectl-ai rejected**: Misses productivity benefits

---

## 11. Logging and Monitoring

### Decision: kubectl logs + metrics-server for Phase IV

**Options Considered**:
1. **kubectl logs only** (basic, no metrics)
2. **kubectl logs + metrics-server** (logs + resource monitoring)
3. **Prometheus + Grafana** (full observability stack)
4. **ELK/Loki stack** (centralized logging)

**Rationale**:
- **kubectl logs + metrics-server selected**:
  - Kubernetes-native: Built-in logging, metrics-server addon
  - Zero setup: metrics-server enabled with `minikube addons enable metrics-server`
  - Sufficient for dev: Can see logs and resource usage
  - Aligned with constitution: Principle VII (Simplicity and Pragmatism)

**Monitoring Commands**:
```bash
# Logs
kubectl logs -f <pod-name>                    # Follow logs
kubectl logs -l app=todo-backend --tail=50    # Last 50 lines by label

# Metrics
kubectl top nodes                             # Node resource usage
kubectl top pods                              # Pod resource usage

# AI-assisted
kubectl-ai "show me logs for failing pods"
kubectl-ai "which pods are using most CPU?"
```

**Out of Scope** (Phase V+):
- Prometheus/Grafana: Advanced metrics visualization
- ELK/Loki: Centralized logging and search
- Distributed tracing: OpenTelemetry, Jaeger

**Alternatives Considered**:
- **Full observability stack rejected**: Over-engineering for local development

---

## 12. Security Practices

### Decision: Non-Root Containers, No Hardcoded Secrets, Base64 Secrets

**Options Considered**:
1. **Root containers** (default, insecure)
2. **Non-root containers** (secure, standard practice)
3. **Read-only filesystem** (maximum security, complex)

**Rationale**:
- **Non-root containers selected**:
  - Security: Reduces attack surface if container compromised
  - Standard practice: Recommended by Docker and Kubernetes
  - Constitution compliance: Principle V (Security by Default)
  - Easy implementation: `USER python` / `USER node` in Dockerfile

**Security Checklist**:
- [x] Non-root users in all Dockerfiles
- [x] Secrets externalized (not in Git, not in Dockerfiles)
- [x] Official base images only
- [x] Resource limits to prevent resource exhaustion
- [x] `.dockerignore` to exclude .env files
- [x] `.gitignore` updated to exclude Kubernetes secrets

**Implementation**:
```dockerfile
# Dockerfile
FROM python:3.11-slim
RUN groupadd -r python && useradd -r -g python python
USER python  # Run as non-root
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Alternatives Considered**:
- **Read-only filesystem rejected**: Complex, requires volume mounts for writable dirs
- **Root containers rejected**: Violates security principles

---

## Summary

All technology decisions align with the Phase IV Constitution principles:
- ✅ Cloud-Native First: Containerized, stateless, 12-factor
- ✅ IaC Mandate: Helm charts as source of truth
- ✅ AI-Assisted DevOps: kubectl-ai for operations, Claude Code for generation
- ✅ Test-First Infrastructure: helm lint, dry-run, deployment validation
- ✅ Security by Default: Non-root, secrets externalized, resource limits
- ✅ Observability: Structured logs, health probes, metrics-server
- ✅ Simplicity: Single Helm chart, NodePort access, no over-engineering

**Next Steps**:
1. Create `data-model.md` (Kubernetes resource definitions)
2. Create `contracts/` (Helm template contracts)
3. Create `quickstart.md` (deployment guide)
4. Run `/sp.tasks` to break plan into implementation tasks
