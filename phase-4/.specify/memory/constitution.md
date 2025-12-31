# Phase IV: Kubernetes Deployment Constitution

## Core Principles

### I. Cloud-Native First
Every component must be designed for cloud-native deployment from the start.

**Requirements:**
- All applications containerized using Docker with multi-stage builds
- Services must be stateless where possible; state externalized to databases/volumes
- 12-Factor App principles: configuration via environment, logs to stdout, port binding
- Health checks (readiness/liveness probes) mandatory for all deployments
- Graceful shutdown handling (SIGTERM) implemented in all services

**Rationale:** Cloud-native design ensures portability across environments (local → staging → production) and enables horizontal scaling.

### II. Infrastructure as Code (IaC) Mandate
All infrastructure, configuration, and deployment manifests must be version-controlled and declarative.

**Requirements:**
- Helm charts as the single source of truth for Kubernetes deployments
- No manual `kubectl apply` commands; all changes via Helm releases
- ConfigMaps for non-sensitive configuration; Secrets for credentials
- Values files for environment-specific overrides (dev, staging, prod)
- Helm chart versioning following SemVer (MAJOR.MINOR.PATCH)

**Rationale:** IaC eliminates configuration drift, enables reproducibility, and provides audit trails for all infrastructure changes.

### III. AI-Assisted DevOps
Leverage AI tools (Gordon, kubectl-ai, kagent) for efficiency while maintaining human oversight.

**AI Tool Usage:**
- **Gordon (Docker AI)**: Dockerfile generation, container optimization, troubleshooting
- **kubectl-ai**: Natural language Kubernetes operations, deployment verification
- **kagent**: Cluster health analysis, resource optimization, performance tuning
- **Claude Code**: Helm chart generation, YAML templating, configuration management

**Human Verification Required:**
- All AI-generated Dockerfiles must be reviewed for security (no hardcoded secrets, appropriate base images)
- Helm charts validated via `helm lint` and `--dry-run` before deployment
- Resource limits/requests validated against application requirements
- Security contexts and network policies reviewed by human

**Rationale:** AI accelerates development but human judgment ensures security, cost-efficiency, and architectural coherence.

### IV. Test-First for Infrastructure (NON-NEGOTIABLE)
Infrastructure changes must be validated before production deployment.

**Testing Hierarchy:**
1. **Helm Lint**: `helm lint` catches YAML syntax errors
2. **Dry-Run Validation**: `helm install --dry-run --debug` validates against Kubernetes API
3. **Local Testing**: Deploy to Minikube, verify all pods Running, test application functionality
4. **Smoke Tests**: Automated tests verify core functionality (health endpoints, database connectivity)
5. **Load Testing** (optional): Verify resource limits under load

**Acceptance Criteria:**
- All pods reach Running state within 2 minutes
- Readiness probes pass for all deployments
- Services expose correct ports and respond to health checks
- Inter-service communication verified (frontend → backend → database)

**Rationale:** Infrastructure bugs are expensive; catching errors early via local testing prevents production outages.

### V. Security by Default
Security must be built into every layer, not added as an afterthought.

**Mandatory Security Practices:**
- **Secrets Management**: No secrets in Git; use Kubernetes Secrets (base64) locally, external secret managers (Vault, AWS Secrets Manager) for production
- **Least Privilege**: Non-root containers (`runAsNonRoot: true`), read-only root filesystem where possible
- **Image Security**: Use official base images; scan with `docker scan` or Trivy before deployment
- **Network Policies**: Restrict pod-to-pod communication to only necessary paths
- **Resource Limits**: Prevent resource exhaustion via CPU/memory limits
- **RBAC**: Service accounts with minimal permissions

**Prohibited:**
- Hardcoded API keys, database passwords, or tokens in code or Dockerfiles
- Running containers as root without justification
- Exposing unnecessary ports or services
- Using `latest` tag for production images (must be versioned)

**Rationale:** Security vulnerabilities in containerized applications can compromise entire clusters; defense-in-depth is mandatory.

### VI. Observability and Debuggability
Every deployment must provide visibility into its health and behavior.

**Required Observability:**
- **Structured Logging**: JSON logs to stdout with severity levels (INFO, WARN, ERROR)
- **Metrics**: Prometheus metrics exposed (HTTP requests, errors, latency, database connections)
- **Distributed Tracing** (Phase V): OpenTelemetry for request tracing across services
- **Health Endpoints**: `/health` (liveness), `/ready` (readiness) for all services
- **Resource Monitoring**: Kubernetes metrics-server enabled in Minikube

**Debugging Tools:**
- `kubectl logs`, `kubectl describe`, `kubectl exec` for troubleshooting
- `kubectl-ai` for natural language debugging ("why is pod crashing?")
- `kagent` for cluster-level analysis

**Rationale:** Observable systems enable rapid troubleshooting and proactive issue detection.

### VII. Simplicity and Pragmatism
Start with the simplest solution that works; avoid premature optimization.

**Principles:**
- Use Minikube for local development (no need for cloud costs initially)
- Single Helm chart for entire application (not one per microservice unless justified)
- NodePort for local access (Ingress only when needed)
- PostgreSQL in-cluster for development (managed DB for production)
- Manual scaling initially; HorizontalPodAutoscaler only when load requires it

**Avoid Over-Engineering:**
- Don't implement service mesh (Istio, Linkerd) without demonstrated need
- Don't use multiple namespaces until application complexity requires isolation
- Don't implement GitOps (ArgoCD, Flux) until manual deployments become bottleneck

**YAGNI (You Aren't Gonna Need It)**: Add complexity only when real requirements emerge, not for hypothetical future needs.

**Rationale:** Premature optimization wastes time and introduces maintenance burden; start simple, iterate based on real needs.

## Technology Stack Requirements

### Containerization Layer
| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Container Runtime | Docker Desktop | 4.53+ | Industry standard, Gordon AI integration, Minikube compatibility |
| Base Images | Python 3.11-slim, Node 18-alpine | Latest stable | Security updates, smaller image sizes |
| Registry | Minikube local registry | N/A | Local development; DockerHub/ECR for production |

### Orchestration Layer
| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Kubernetes | Minikube | 1.32+ | Local K8s cluster, zero cloud costs |
| Package Manager | Helm | 3.13+ | Templating, versioning, rollback capabilities |
| CLI | kubectl | 1.28+ | Standard K8s CLI |

### AI DevOps Tools
| Tool | Purpose | Required? | OpenAI Key? |
|------|---------|-----------|-------------|
| Gordon (Docker AI) | Docker assistance | Optional | No |
| kubectl-ai | Natural language K8s commands | Recommended | Yes (reuse from chatbot) |
| kagent | Cluster analysis | Optional | Varies by provider |
| Claude Code | Helm chart generation | Mandatory | No |

### Application Stack (Unchanged from Phase III)
| Component | Technology | Port | Image Tag |
|-----------|-----------|------|-----------|
| Todo Frontend | Next.js 14 | 3000 | todo-frontend:v1 |
| Todo Backend | FastAPI | 8000 | todo-backend:v1 |
| Chatbot Frontend | Next.js 14 | 3001 | chatbot-frontend:v1 |
| Chatbot Backend | FastAPI | 8001 | chatbot-backend:v1 |
| Database | PostgreSQL 15 | 5432 | postgres:15-alpine |

## Development Workflow (Agentic Dev Stack)

### Phase IV Workflow: Spec → Plan → Tasks → Implement

**Stage 1: Specification (You Are Here)**
- **Owner**: User + Claude Code
- **Deliverable**: This constitution + Phase IV requirements
- **Acceptance**: User approval of principles and technology stack

**Stage 2: Planning**
- **Owner**: Claude Code (Plan Agent)
- **Input**: PHASE_IV_INSTRUCTIONS.md + Constitution
- **Deliverable**: Architecture plan with:
  - Directory structure for Helm charts
  - Dockerfile specifications for each component
  - Helm templates breakdown (deployments, services, configmaps, secrets)
  - Environment variable mapping
  - Service dependencies and startup order
- **Acceptance**: User approval of plan before implementation

**Stage 3: Task Breakdown**
- **Owner**: Claude Code
- **Deliverable**: Testable tasks in priority order:
  1. Create Dockerfiles for all components
  2. Build and test Docker images locally
  3. Load images into Minikube
  4. Create Helm chart structure (Chart.yaml, values.yaml)
  5. Generate Kubernetes manifests (deployments, services, configmaps, secrets)
  6. Deploy to Minikube via Helm
  7. Verify deployment (all pods Running)
  8. Test application functionality (smoke tests)
  9. Document access URLs and troubleshooting
- **Acceptance**: Each task has clear success criteria and validation steps

**Stage 4: Implementation**
- **Owner**: Claude Code + User (via prompts)
- **Process**:
  1. User provides spec/requirements
  2. Claude Code generates code/config
  3. User reviews and tests locally
  4. Iterate until acceptance criteria met
  5. User approves and commits changes
- **Validation**: All quality gates passed (see below)

**No Manual Coding Allowed**: All code generation via Claude Code prompts; user reviews but does not write implementation.

## Quality Gates

### Gate 1: Dockerfile Validation
**Criteria:**
- [ ] Multi-stage builds for frontend (build + runtime stages)
- [ ] Non-root user specified (`USER node` or `USER python`)
- [ ] `.dockerignore` excludes unnecessary files (node_modules, .git, .env)
- [ ] Health check instruction present (HEALTHCHECK or app-level)
- [ ] No secrets in environment variables or layers
- [ ] Builds successfully: `docker build -t <image>:v1 .`

**Verification:**
```bash
docker build -t <image>:v1 .  # Must succeed
docker run --rm <image>:v1    # Must start without errors
docker scan <image>:v1        # No critical vulnerabilities
```

### Gate 2: Helm Chart Validation
**Criteria:**
- [ ] `helm lint` passes with zero errors
- [ ] `helm install --dry-run --debug` succeeds
- [ ] All required values templated (no hardcoded image tags, ports)
- [ ] Secrets properly externalized (not in values.yaml)
- [ ] Resource limits defined for all containers
- [ ] Probes configured (readinessProbe, livenessProbe)
- [ ] Labels consistent across all resources

**Verification:**
```bash
helm lint ./todo-app
helm install todo-app ./todo-app --dry-run --debug
```

### Gate 3: Deployment Validation
**Criteria:**
- [ ] All pods reach Running state within 2 minutes
- [ ] Readiness probes pass (pod shows READY 1/1 or 2/2)
- [ ] Services have endpoints: `kubectl get endpoints`
- [ ] No CrashLoopBackOff, ImagePullBackOff, or Error states
- [ ] Logs show successful startup (no uncaught exceptions)

**Verification:**
```bash
kubectl get pods              # All Running
kubectl get services          # All have CLUSTER-IP
kubectl get deployments       # READY matches DESIRED
kubectl logs <pod-name>       # No errors
```

### Gate 4: Functional Validation
**Criteria:**
- [ ] Frontend accessible via browser (Minikube IP + NodePort)
- [ ] Backend API responds to health check: `curl http://<minikube-ip>:<port>/health`
- [ ] Database connectivity verified (backend logs show successful connection)
- [ ] Core functionality works (create task, list tasks, delete task)
- [ ] Chatbot functionality works (AI responses, task creation via chat)

**Verification:**
```bash
minikube service todo-frontend    # Opens in browser
curl http://$(minikube ip):30000/api/health  # Returns 200 OK
# Manual testing: Create/delete tasks in UI
```

### Gate 5: Documentation and Cleanup
**Criteria:**
- [ ] README.md updated with deployment instructions
- [ ] Environment variables documented (which keys required)
- [ ] Access URLs documented (how to reach frontend/backend)
- [ ] Troubleshooting guide included (common errors and fixes)
- [ ] Cleanup instructions documented (helm uninstall, minikube delete)
- [ ] All generated files committed to Git (Dockerfiles, Helm charts)

## Governance

### Constitution Authority
- This constitution supersedes all other development practices for Phase IV
- Deviations require documented justification and user approval
- Amendments must be versioned and ratified

### Review and Compliance
- All Helm charts reviewed against principles before deployment
- Security checklist completed for all Docker images
- Quality gates validated and documented
- Claude Code must reference this constitution when generating artifacts

### Amendment Process
1. Propose amendment with rationale and impact analysis
2. User approval required for principle changes
3. Update version and last amended date
4. Document in ADR if architecturally significant
5. Communicate changes to all stakeholders

### Success Metrics
Phase IV is complete when:
- [ ] All 4 applications (todo frontend/backend, chatbot frontend/backend) + PostgreSQL deployed to Minikube
- [ ] Helm chart successfully installs/upgrades/rollsback application
- [ ] All quality gates passed (Dockerfile, Helm, Deployment, Functional)
- [ ] Application accessible via browser and fully functional
- [ ] Documentation complete (README, troubleshooting, cleanup)
- [ ] User validates deployment and approves for production readiness

### Risk Management
**Top Risks:**
1. **Image Pull Errors**: Mitigate via `imagePullPolicy: Never` and local image loading
2. **Resource Exhaustion**: Mitigate via resource limits and Minikube sizing (4 CPU, 8GB RAM)
3. **Database Persistence Loss**: Mitigate via PersistentVolumeClaims (5Gi for PostgreSQL)
4. **Secret Exposure**: Mitigate via .gitignore for .env files, Kubernetes Secrets for deployment
5. **Service Communication Failures**: Mitigate via service discovery (DNS), health checks, retries

**Kill Switches:**
- `helm rollback <release> <revision>` for bad deployments
- `helm uninstall <release>` for complete removal
- `minikube delete` for cluster corruption

## References
- [PHASE_IV_INSTRUCTIONS.md](../../../PHASE_IV_INSTRUCTIONS.md) - Deployment guide
- [12-Factor App](https://12factor.net/) - Cloud-native principles
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

---

**Version**: 1.0.0
**Ratified**: 2025-12-30
**Last Amended**: 2025-12-30
**Phase**: IV - Local Kubernetes Deployment
**Status**: Active
