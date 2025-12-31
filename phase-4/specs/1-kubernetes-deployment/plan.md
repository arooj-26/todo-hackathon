# Implementation Plan: Kubernetes Deployment for Todo Chatbot

**Branch**: `1-kubernetes-deployment` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/1-kubernetes-deployment/spec.md`

## Summary

Deploy the Todo Chatbot application (2 frontends, 2 backends, PostgreSQL database) to a local Kubernetes cluster using Helm charts, Docker containerization, and AI-assisted DevOps tools (Gordon, kubectl-ai, kagent). The deployment will leverage Minikube for local Kubernetes, multi-stage Docker builds for optimization, and Infrastructure as Code via Helm for version-controlled, repeatable deployments. The primary technical approach is Cloud-Native First with Test-First Infrastructure validation, ensuring all pods reach Running state and application functionality is preserved post-deployment.

---

## Technical Context

**Language/Version**:
- **Backend**: Python 3.11 (FastAPI applications)
- **Frontend**: Node 18 (Next.js applications)
- **Infrastructure**: Kubernetes 1.28+, Helm 3.13+, Docker 24.0+

**Primary Dependencies**:
- **Containerization**: Docker Desktop 4.53+, Dockerfiles (multi-stage builds)
- **Orchestration**: Minikube 1.32+, kubectl 1.28+, Helm 3.13+
- **AI DevOps**: kubectl-ai (OpenAI API), Gordon (Docker AI), kagent (optional)
- **Application Stack** (from Phase III):
  - Todo Backend: FastAPI, SQLModel, PostgreSQL (psycopg[binary]), python-jose, passlib
  - Todo Frontend: Next.js 14, React, TailwindCSS, Axios
  - Chatbot Backend: FastAPI, SQLModel, PostgreSQL, OpenAI, MCP SDK
  - Chatbot Frontend: Next.js 14, React, OpenAI ChatKit

**Storage**:
- **Development**: PostgreSQL 15-alpine in Kubernetes pod with PersistentVolumeClaim (5Gi)
- **Production** (future): Neon Serverless PostgreSQL or managed database service
- **Images**: Minikube local registry (`imagePullPolicy: Never`)

**Testing**:
- **Infrastructure**: `helm lint`, `helm install --dry-run --debug`
- **Deployment**: `kubectl get pods`, `kubectl describe pod`, `kubectl logs`
- **Functional**: Manual testing via browser (create/delete tasks), health endpoint checks
- **AI-Assisted**: `kubectl-ai "are all pods running?"`, `kubectl-ai "show logs for failing pods"`

**Target Platform**:
- **Development**: Minikube on local machine (Windows/macOS/Linux)
- **Cluster**: Docker driver, 4 CPU cores, 8GB RAM
- **Access**: NodePort services (30000 for Todo frontend, 30001 for Chatbot frontend)

**Project Type**:
- **Multi-service web application** with separate frontend/backend for two applications
- **Infrastructure as Code** (Helm charts) for deployment
- **Cloud-native** architecture with stateless services and externalized configuration

**Performance Goals**:
- All pods reach Running state within 2 minutes of `helm install`
- Frontend applications load in browser within 3 seconds
- API responses (task CRUD) complete within 1 second
- Docker images under 500MB each (optimized with multi-stage builds)
- Chatbot responses within 5 seconds (including AI processing)

**Constraints**:
- **Local-only deployment**: No cloud provider integration in Phase IV
- **Resource limits**: 4 CPU cores, 8GB RAM total for Minikube
- **Image registry**: Local Minikube registry only (no DockerHub push)
- **Secrets**: Managed via Kubernetes Secrets with base64 encoding (no external secret managers)
- **Networking**: NodePort for external access (no Ingress controller initially)
- **Scaling**: Manual scaling only (no HorizontalPodAutoscaler in Phase IV)
- **Monitoring**: kubectl logs and metrics-server only (no Prometheus/Grafana yet)

**Scale/Scope**:
- **Services**: 5 Kubernetes deployments (2 frontends @ 2 replicas, 2 backends @ 1 replica, 1 database @ 1 replica)
- **Containers**: 4 custom Docker images + 1 official PostgreSQL image
- **Helm Chart**: Single chart with ~13 template files
- **Environment Variables**: ~15 configuration values (database URLs, API keys, service URLs)
- **Users**: Development/testing environment (10 concurrent users target)
- **Data**: Small datasets (tasks, conversations) with persistence via PVC

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Adherence

✅ **I. Cloud-Native First**
- Applications containerized using Docker with multi-stage builds
- Services stateless where possible (frontends, backends stateless; database state externalized to PVC)
- 12-Factor App principles: configuration via environment (Helm values), logs to stdout, port binding
- Health checks (readinessProbe, livenessProbe) mandatory for all deployments
- Graceful shutdown handling (SIGTERM) implemented in FastAPI and Next.js

✅ **II. Infrastructure as Code (IaC) Mandate**
- Helm charts as single source of truth for Kubernetes deployments
- No manual `kubectl apply` commands; all changes via `helm install/upgrade`
- ConfigMaps for non-sensitive configuration; Secrets for credentials
- Values files for environment-specific overrides
- Helm chart versioning following SemVer (1.0.0 initial)

✅ **III. AI-Assisted DevOps**
- **Claude Code**: Generates Dockerfiles and Helm charts (primary tool)
- **kubectl-ai**: Natural language Kubernetes operations (deployment verification, troubleshooting)
- **Gordon**: Docker AI for Dockerfile optimization and container troubleshooting (optional)
- **kagent**: Cluster health analysis and resource optimization (optional)
- **Human verification required**: All AI-generated Dockerfiles reviewed for security, Helm charts validated via `helm lint`

✅ **IV. Test-First for Infrastructure**
- Helm Lint: `helm lint k8s/helm-charts/todo-app` catches YAML syntax errors
- Dry-Run Validation: `helm install --dry-run --debug` validates against Kubernetes API
- Local Testing: Deploy to Minikube, verify all pods Running, test application functionality
- Smoke Tests: Health endpoints, database connectivity, inter-service communication
- **Acceptance**: All pods Running within 2 minutes, readiness probes passing, application functional

✅ **V. Security by Default**
- **Secrets Management**: No secrets in Git; Kubernetes Secrets with base64; .gitignore for .env files
- **Least Privilege**: Non-root containers (`USER node`, `USER python`), read-only root filesystem where feasible
- **Image Security**: Official base images (python:3.11-slim, node:18-alpine, postgres:15-alpine)
- **Resource Limits**: CPU/memory limits prevent resource exhaustion (500m CPU, 512Mi memory per container)
- **Prohibited**: Hardcoded API keys, running as root, using `latest` tag

✅ **VI. Observability and Debuggability**
- **Structured Logging**: JSON logs to stdout with severity levels (FastAPI logging, Next.js console)
- **Health Endpoints**: `/health` (liveness), `/ready` (readiness) for all services
- **Resource Monitoring**: Kubernetes metrics-server enabled in Minikube
- **Debugging Tools**: `kubectl logs`, `kubectl describe`, `kubectl exec`, `kubectl-ai` for natural language debugging

✅ **VII. Simplicity and Pragmatism**
- Use Minikube for local development (no cloud costs)
- Single Helm chart for entire application (not one per microservice)
- NodePort for local access (Ingress only when needed)
- PostgreSQL in-cluster for development (managed DB for production later)
- Manual scaling initially; HorizontalPodAutoscaler only when load requires it
- **YAGNI**: No service mesh, no GitOps, no multi-namespace complexity yet

### Quality Gates

All quality gates defined in constitution must pass before declaring Phase IV complete:

**Gate 1: Dockerfile Validation** (FR-001 to FR-007)
- Multi-stage builds for frontends
- Non-root user specified
- .dockerignore excludes unnecessary files
- Health check instruction or app-level endpoint
- No secrets in environment or layers
- Builds successfully

**Gate 2: Helm Chart Validation** (FR-008 to FR-020)
- `helm lint` passes with zero errors
- `helm install --dry-run --debug` succeeds
- All values templated (no hardcoded tags/ports)
- Secrets externalized
- Resource limits defined
- Probes configured
- Labels consistent

**Gate 3: Deployment Validation** (FR-021 to FR-030)
- All pods Running within 2 minutes
- Readiness probes pass (READY 1/1 or 2/2)
- Services have endpoints
- No CrashLoopBackOff or Error states
- Logs show successful startup

**Gate 4: Functional Validation** (FR-029, SC-005, SC-006)
- Frontends accessible via browser
- Backend APIs respond to health checks
- Database connectivity verified
- Core functionality works (create/delete tasks)
- Chatbot functionality works

**Gate 5: Documentation** (SC-015)
- README updated with deployment instructions
- Environment variables documented
- Access URLs documented
- Troubleshooting guide included
- Cleanup instructions documented

### Violations and Justifications

None - all architecture decisions align with constitution principles.

---

## Project Structure

### Documentation (this feature)

```text
phase-4/specs/1-kubernetes-deployment/
├── spec.md                      # Feature specification (COMPLETE)
├── plan.md                      # This file - architectural plan
├── research.md                  # Technology decisions and rationale
├── data-model.md                # Kubernetes resources and relationships
├── quickstart.md                # Deployment quickstart guide
├── contracts/                   # Helm chart templates structure
│   ├── helm-chart-structure.md # Chart.yaml and values.yaml schemas
│   ├── deployment-template.md  # Deployment resource template pattern
│   ├── service-template.md     # Service resource template pattern
│   ├── configmap-template.md   # ConfigMap resource template pattern
│   └── secret-template.md      # Secret resource template pattern
├── checklists/
│   └── requirements.md          # Spec quality validation (COMPLETE)
└── tasks.md                     # Implementation tasks (NEXT - /sp.tasks command)
```

### Source Code (repository root)

```text
D:\web-todo/
├── phase-4/                     # Phase IV specific files
│   ├── .specify/                # SpecKit Plus framework
│   ├── specs/                   # Feature specifications
│   └── history/                 # PHRs and ADRs
│
├── k8s/                         # ⭐ NEW - Kubernetes manifests
│   └── helm-charts/             # Helm charts directory
│       └── todo-app/            # Main application chart
│           ├── Chart.yaml       # Chart metadata
│           ├── values.yaml      # Default configuration values
│           ├── .helmignore      # Helm ignore patterns
│           ├── templates/       # Kubernetes resource templates
│           │   ├── _helpers.tpl              # Template helpers
│           │   ├── configmap.yaml            # Application config
│           │   ├── secrets.yaml              # Sensitive data
│           │   ├── postgresql-pvc.yaml       # Database storage
│           │   ├── postgresql-deployment.yaml
│           │   ├── postgresql-service.yaml
│           │   ├── todo-backend-deployment.yaml
│           │   ├── todo-backend-service.yaml
│           │   ├── todo-frontend-deployment.yaml
│           │   ├── todo-frontend-service.yaml
│           │   ├── chatbot-backend-deployment.yaml
│           │   ├── chatbot-backend-service.yaml
│           │   ├── chatbot-frontend-deployment.yaml
│           │   └── chatbot-frontend-service.yaml
│           ├── charts/          # Chart dependencies (if any)
│           └── README.md        # Chart documentation
│
├── todo-application/
│   ├── backend/
│   │   ├── app/                 # FastAPI application
│   │   ├── requirements.txt
│   │   ├── Dockerfile           # ⭐ NEW - Backend container
│   │   └── .dockerignore        # ⭐ NEW - Docker ignore
│   └── frontend/
│       ├── src/                 # Next.js application
│       ├── package.json
│       ├── Dockerfile           # ⭐ NEW - Frontend container
│       └── .dockerignore        # ⭐ NEW - Docker ignore
│
├── chatbot/
│   ├── backend/
│   │   ├── src/                 # FastAPI application
│   │   ├── requirements.txt
│   │   ├── Dockerfile           # ⭐ NEW - Chatbot backend container
│   │   └── .dockerignore        # ⭐ NEW - Docker ignore
│   └── frontend/
│       ├── src/                 # Next.js application
│       ├── package.json
│       ├── Dockerfile           # ⭐ NEW - Chatbot frontend container
│       └── .dockerignore        # ⭐ NEW - Docker ignore
│
├── .gitignore                   # Updated to exclude Kubernetes secrets
├── README.md                    # Updated with Phase IV deployment
└── PHASE_IV_INSTRUCTIONS.md     # Deployment guide (EXISTS)
```

**Structure Decision**:
We chose **Option 2: Web application** structure with separate `k8s/` directory for Kubernetes manifests. This aligns with the existing project structure (separate backend/frontend directories for todo-application and chatbot) and follows best practices for Infrastructure as Code by keeping deployment manifests separate from application code.

**Rationale**:
- **Separation of Concerns**: Application code (todo-application/, chatbot/) remains unchanged; deployment infrastructure in k8s/
- **Reusability**: Same Helm chart can deploy to different environments (dev, staging, prod) with different values
- **Version Control**: Kubernetes manifests versioned alongside application code for consistency
- **Discoverability**: k8s/ at root makes deployment configuration immediately visible
- **Helm Best Practice**: Standard chart structure (`Chart.yaml`, `values.yaml`, `templates/`) follows Helm conventions

---

## Complexity Tracking

> **No violations - table not needed.**

All architectural decisions comply with constitution principles. No complexity introduced that requires justification.

---

## Architecture Overview

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Local Machine (Developer Workstation)                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Docker Desktop 4.53+                                       │ │
│  │  ├─ Docker Daemon (build images)                           │ │
│  │  └─ Gordon AI (optional - Dockerfile assistance)           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Minikube Cluster (4 CPU, 8GB RAM)                         │ │
│  │                                                              │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Namespace: default                                   │  │ │
│  │  │                                                        │  │ │
│  │  │  ┌─────────────────┐    ┌─────────────────┐         │  │ │
│  │  │  │ Todo Frontend   │    │ Chatbot Frontend│         │  │ │
│  │  │  │ (Next.js)       │    │ (Next.js)       │         │  │ │
│  │  │  │ Port: 3000      │    │ Port: 3001      │         │  │ │
│  │  │  │ Replicas: 2     │    │ Replicas: 2     │         │  │ │
│  │  │  │ NodePort: 30000 │    │ NodePort: 30001 │         │  │ │
│  │  │  └────────┬────────┘    └────────┬────────┘         │  │ │
│  │  │           │                      │                   │  │ │
│  │  │  ┌────────▼────────┐    ┌───────▼─────────┐         │  │ │
│  │  │  │ Todo Backend    │    │ Chatbot Backend │         │  │ │
│  │  │  │ (FastAPI)       │    │ (FastAPI)       │         │  │ │
│  │  │  │ Port: 8000      │    │ Port: 8001      │         │  │ │
│  │  │  │ Replicas: 1     │    │ Replicas: 1     │         │  │ │
│  │  │  │ ClusterIP       │    │ ClusterIP       │         │  │ │
│  │  │  └────────┬────────┘    └────────┬────────┘         │  │ │
│  │  │           │                      │                   │  │ │
│  │  │           └──────────┬───────────┘                   │  │ │
│  │  │                      │                               │  │ │
│  │  │           ┌──────────▼──────────┐                    │  │ │
│  │  │           │ PostgreSQL          │                    │  │ │
│  │  │           │ (postgres:15-alpine)│                    │  │ │
│  │  │           │ Port: 5432          │                    │  │ │
│  │  │           │ Replicas: 1         │                    │  │ │
│  │  │           │ ClusterIP           │                    │  │ │
│  │  │           │ PVC: 5Gi            │                    │  │ │
│  │  │           └─────────────────────┘                    │  │ │
│  │  │                                                        │  │ │
│  │  │  ┌────────────────────────────────────────────────┐  │  │ │
│  │  │  │ ConfigMap: app-config                          │  │  │ │
│  │  │  │ - DATABASE_HOST, TODO_API_URL, ports          │  │  │ │
│  │  │  └────────────────────────────────────────────────┘  │  │ │
│  │  │                                                        │  │ │
│  │  │  ┌────────────────────────────────────────────────┐  │  │ │
│  │  │  │ Secret: app-secrets                            │  │  │ │
│  │  │  │ - POSTGRES_PASSWORD, OPENAI_API_KEY, JWT keys │  │  │ │
│  │  │  └────────────────────────────────────────────────┘  │  │ │
│  │  │                                                        │  │ │
│  │  │  ┌────────────────────────────────────────────────┐  │  │ │
│  │  │  │ PersistentVolumeClaim: postgres-pvc (5Gi)     │  │  │ │
│  │  │  └────────────────────────────────────────────────┘  │  │ │
│  │  │                                                        │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  kubectl / kubectl-ai / Helm CLI                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Browser: http://<minikube-ip>:30000 (Todo)                │ │
│  │           http://<minikube-ip>:30001 (Chatbot)             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Service Communication Flow

```
User Browser
    │
    ├──── http://<minikube-ip>:30000 ────► Todo Frontend Service (NodePort)
    │                                         │
    │                                         ▼
    │                                      Todo Frontend Pod(s)
    │                                         │
    │                                         │ HTTP GET/POST /api/*
    │                                         ▼
    │                                      Todo Backend Service (ClusterIP)
    │                                         │
    │                                         ▼
    │                                      Todo Backend Pod
    │                                         │
    │                                         │ PostgreSQL queries
    │                                         ▼
    │                                      PostgreSQL Service (ClusterIP)
    │                                         │
    │                                         ▼
    │                                      PostgreSQL Pod (with PVC)
    │
    └──── http://<minikube-ip>:30001 ────► Chatbot Frontend Service (NodePort)
                                              │
                                              ▼
                                           Chatbot Frontend Pod(s)
                                              │
                                              │ HTTP POST /api/chat
                                              ▼
                                           Chatbot Backend Service (ClusterIP)
                                              │
                                              ▼
                                           Chatbot Backend Pod
                                              │
                                              ├──► OpenAI API (external, HTTPS)
                                              │
                                              ├──► Todo Backend Service (HTTP, MCP tools)
                                              │
                                              └──► PostgreSQL Service (PostgreSQL, conversations)
```

---

## Phase 0: Research & Technology Decisions

**Documented in**: [research.md](./research.md) (to be created)

Key research areas:
1. **Docker Base Images**: python:3.11-slim vs python:3.11-alpine, node:18-alpine vs node:18-slim
2. **Helm Chart Best Practices**: Template helpers, values structure, naming conventions
3. **Health Probe Configuration**: Readiness vs liveness, HTTP vs exec probes, thresholds
4. **Resource Limits**: CPU/memory sizing for FastAPI and Next.js applications
5. **PostgreSQL in Kubernetes**: StatefulSet vs Deployment, PVC configuration, backup strategies
6. **Environment Variable Management**: ConfigMap vs Secret, Helm templating patterns
7. **kubectl-ai Best Practices**: Common commands, natural language patterns, error handling
8. **Docker Multi-Stage Builds**: Build stage vs runtime stage, layer caching optimization

---

## Phase 1: Design & Contracts

**Data Model**: [data-model.md](./data-model.md) (to be created)

Key entities:
- Docker Image (name, tag, base image, layers, size)
- Helm Chart (name, version, app version, values schema)
- Deployment (replicas, selector, pod template spec, resource limits, probes)
- Service (type, selector, ports, ClusterIP/NodePort)
- ConfigMap (data key-value pairs)
- Secret (data key-value pairs, base64 encoded)
- PersistentVolumeClaim (size, access mode, storage class)
- Container (image, ports, env vars, resource requests/limits)

**API Contracts**: [contracts/](./contracts/) (to be created)

Key contracts:
- Helm Chart Structure (`Chart.yaml`, `values.yaml` schemas)
- Deployment Template Pattern (common fields, resource limits, probes)
- Service Template Pattern (service types, port mappings)
- ConfigMap Template Pattern (configuration data structure)
- Secret Template Pattern (sensitive data structure)

**Quickstart**: [quickstart.md](./quickstart.md) (to be created)

Deployment guide covering:
1. Prerequisites installation
2. Building Docker images
3. Loading images into Minikube
4. Installing Helm chart
5. Verifying deployment
6. Accessing applications
7. Troubleshooting common issues

---

## Implementation Phases

### Phase 2: Dockerfile Creation (Tasks 1-16)

**Deliverables**:
- `todo-application/backend/Dockerfile` (multi-stage: build + runtime)
- `todo-application/backend/.dockerignore`
- `todo-application/frontend/Dockerfile` (multi-stage: build + runtime)
- `todo-application/frontend/.dockerignore`
- `chatbot/backend/Dockerfile` (multi-stage: build + runtime)
- `chatbot/backend/.dockerignore`
- `chatbot/frontend/Dockerfile` (multi-stage: build + runtime)
- `chatbot/frontend/.dockerignore`

**Success Criteria**:
- All 4 Dockerfiles build successfully
- Images under 500MB each
- Non-root users configured
- Health check endpoints accessible
- No secrets in image layers

### Phase 3: Helm Chart Structure (Tasks 17-30)

**Deliverables**:
- `k8s/helm-charts/todo-app/Chart.yaml`
- `k8s/helm-charts/todo-app/values.yaml`
- `k8s/helm-charts/todo-app/.helmignore`
- `k8s/helm-charts/todo-app/README.md`
- `k8s/helm-charts/todo-app/templates/_helpers.tpl`

**Success Criteria**:
- `helm lint` passes
- Chart metadata correct (name, version, description)
- Values schema comprehensive
- Helpers reusable

### Phase 4: Kubernetes Resource Templates (Tasks 31-50)

**Deliverables**:
- ConfigMap template (`templates/configmap.yaml`)
- Secret template (`templates/secrets.yaml`)
- PostgreSQL PVC template (`templates/postgresql-pvc.yaml`)
- PostgreSQL Deployment template (`templates/postgresql-deployment.yaml`)
- PostgreSQL Service template (`templates/postgresql-service.yaml`)
- Todo Backend Deployment + Service templates
- Todo Frontend Deployment + Service templates
- Chatbot Backend Deployment + Service templates
- Chatbot Frontend Deployment + Service templates

**Success Criteria**:
- `helm install --dry-run --debug` succeeds
- All templates render correctly
- Resource limits defined
- Probes configured
- Labels consistent

### Phase 5: Deployment and Validation (Tasks 51-70)

**Deliverables**:
- All pods Running
- All services accessible
- Application functional
- Documentation complete

**Success Criteria**:
- Deployment completes in under 2 minutes
- All quality gates pass (Gates 1-5)
- Success criteria met (SC-001 to SC-015)

---

## Risk Analysis

### Risk 1: Image Pull Errors in Minikube
**Severity**: High | **Likelihood**: High
**Mitigation**: Set `imagePullPolicy: Never`, use `eval $(minikube docker-env)`, document image loading
**Fallback**: `minikube image load <image>:<tag>`

### Risk 2: Resource Exhaustion in Minikube
**Severity**: High | **Likelihood**: Medium
**Mitigation**: Start Minikube with 4 CPU/8GB RAM, define resource limits, monitor with `kubectl top`
**Fallback**: Reduce replica counts, reduce resource requests

### Risk 3: Database Persistence Loss
**Severity**: Medium | **Likelihood**: Medium
**Mitigation**: Configure PersistentVolumeClaim, test pod restart
**Fallback**: Accept data loss in dev environment

### Risk 4: Secret Exposure in Git
**Severity**: Critical | **Likelihood**: Medium
**Mitigation**: .gitignore for .env, Kubernetes Secrets with templated values, git-secrets tool
**Fallback**: Rotate secrets, `git filter-branch` to remove

### Risk 5: Service Communication Failures
**Severity**: Medium | **Likelihood**: Medium
**Mitigation**: Use Kubernetes DNS, test with `kubectl exec` + curl, proper selectors/labels, readiness probes
**Fallback**: Use ClusterIP addresses directly

---

## Next Steps

1. ✅ **Specification Complete** - `spec.md` created and validated
2. ✅ **Plan Complete** - This document
3. **Create Supporting Documents**:
   - `research.md` - Technology decisions and rationale
   - `data-model.md` - Kubernetes resource definitions
   - `contracts/` - Helm chart template contracts
   - `quickstart.md` - Deployment quickstart guide
4. **Task Breakdown**: Run `/sp.tasks` to create implementation tasks
5. **Implementation**: Execute tasks using Claude Code
6. **Validation**: Test against all quality gates
7. **Documentation**: Update README with Phase IV outcomes

---

**Status**: Planning Complete - Ready for Task Breakdown
**Next Command**: `/sp.tasks`

📋 **Architectural Decision Detected**: Docker base image selection (python:3.11-slim vs alpine), Helm chart structure (single chart vs multiple charts), Resource limit allocation (CPU/memory per service). Document reasoning and tradeoffs? Run `/sp.adr docker-helm-architecture-decisions`
