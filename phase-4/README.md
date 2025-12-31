# Phase IV: Local Kubernetes Deployment - Project Overview

## Quick Links
- **[Constitution](./.specify/memory/constitution.md)** - Core principles and governance
- **[Instructions](../PHASE_IV_INSTRUCTIONS.md)** - Step-by-step deployment guide
- **[Claude Rules](./CLAUDE.md)** - AI agent development guidelines

---

## Phase IV Objective

Deploy the **Todo Chatbot Application** to a local Kubernetes cluster using:
- **Minikube** (local K8s cluster)
- **Helm Charts** (package management)
- **Docker** (containerization)
- **AI DevOps Tools** (Gordon, kubectl-ai, kagent)

Following the **Agentic Dev Stack** workflow: **Spec → Plan → Tasks → Implement** (No manual coding!)

---

## What You'll Deploy

### Application Components
| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| Todo Frontend | Next.js 14 | 3000 | Task management UI |
| Todo Backend | FastAPI | 8000 | RESTful API for tasks |
| Chatbot Frontend | Next.js 14 | 3001 | AI chat interface |
| Chatbot Backend | FastAPI | 8001 | AI agent with MCP tools |
| PostgreSQL | PostgreSQL 15 | 5432 | Database for both apps |

### Infrastructure Stack
- **Docker Desktop 4.53+** - Containerization with Gordon AI
- **Minikube 1.32+** - Local Kubernetes cluster
- **Helm 3.13+** - Kubernetes package manager
- **kubectl 1.28+** - Kubernetes CLI
- **kubectl-ai** - Natural language K8s commands
- **kagent** (optional) - Cluster analysis and optimization

---

## Project Structure

```
phase-4/
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # ⭐ Core principles and governance
│   ├── templates/                   # Spec, plan, task templates
│   └── scripts/                     # Automation scripts
├── specs/                           # Feature specifications (to be created)
├── history/
│   ├── prompts/                     # Prompt History Records
│   └── adr/                         # Architecture Decision Records
├── CLAUDE.md                        # AI agent rules and workflow
└── README.md                        # This file

Root level:
├── PHASE_IV_INSTRUCTIONS.md         # Detailed deployment guide
├── k8s/                             # Kubernetes manifests (to be created)
│   └── helm-charts/
│       └── todo-app/                # Helm chart for entire application
├── todo-application/
│   ├── backend/                     # FastAPI backend
│   │   └── Dockerfile               # (to be created)
│   └── frontend/                    # Next.js frontend
│       └── Dockerfile               # (to be created)
└── chatbot/
    ├── backend/                     # FastAPI chatbot
    │   └── Dockerfile               # (to be created)
    └── frontend/                    # Next.js chatbot UI
        └── Dockerfile               # (to be created)
```

---

## Constitution Highlights

### 7 Core Principles

1. **Cloud-Native First** - 12-Factor apps, stateless services, health checks mandatory
2. **Infrastructure as Code** - Helm charts as single source of truth, no manual kubectl
3. **AI-Assisted DevOps** - Use Gordon, kubectl-ai, kagent with human oversight
4. **Test-First Infrastructure** - Helm lint → dry-run → Minikube → smoke tests
5. **Security by Default** - No secrets in Git, non-root containers, image scanning
6. **Observability** - Structured logs, health endpoints, metrics, debugging tools
7. **Simplicity & Pragmatism** - Start simple, avoid over-engineering (YAGNI)

### Quality Gates (All Must Pass)

✅ **Gate 1: Dockerfile Validation** - Multi-stage builds, non-root, no secrets
✅ **Gate 2: Helm Chart Validation** - Lint passes, dry-run succeeds, templates correct
✅ **Gate 3: Deployment Validation** - All pods Running, probes pass, no errors
✅ **Gate 4: Functional Validation** - UI accessible, APIs respond, chatbot works
✅ **Gate 5: Documentation** - README, env vars, URLs, troubleshooting documented

---

## Development Workflow (Agentic Dev Stack)

### Stage 1: Specification ✅ (COMPLETE)
- [x] Constitution created (`.specify/memory/constitution.md`)
- [x] Instructions reviewed (`PHASE_IV_INSTRUCTIONS.md`)
- [ ] **Next**: User approval of principles

### Stage 2: Planning (NEXT)
**What happens:**
- Claude Code (Plan Agent) explores codebase
- Creates architecture plan in `specs/kubernetes-deployment/plan.md`
- Defines directory structure, Dockerfile specs, Helm templates
- Maps environment variables and service dependencies

**User Action Required:** Approve plan before implementation

### Stage 3: Task Breakdown
**What happens:**
- Claude Code breaks plan into testable tasks
- Creates `specs/kubernetes-deployment/tasks.md`
- Each task has clear success criteria

**Tasks Preview:**
1. Create Dockerfiles for all 4 components + .dockerignore
2. Build and test Docker images locally
3. Load images into Minikube
4. Create Helm chart structure (Chart.yaml, values.yaml)
5. Generate K8s manifests (deployments, services, configmaps, secrets)
6. Deploy to Minikube via Helm
7. Verify deployment (all pods Running)
8. Test application functionality
9. Document deployment and troubleshooting

### Stage 4: Implementation
**What happens:**
- User prompts Claude Code: "Implement task 1"
- Claude Code generates Dockerfiles
- User reviews and tests: `docker build -t todo-backend:v1 .`
- Iterate until quality gates pass
- Repeat for each task

**No Manual Coding:** User provides prompts, Claude Code generates all code/config

---

## Getting Started

### 1. Review the Constitution
```bash
# Read the constitution to understand principles
cat phase-4/.specify/memory/constitution.md
```

**Key Questions to Answer:**
- Do you agree with the 7 core principles?
- Any technology stack changes needed?
- Any additional security/compliance requirements?

### 2. Check Prerequisites
Ensure you have these tools installed:
- [ ] Docker Desktop 4.53+ (with Gordon enabled)
- [ ] Minikube 1.32+
- [ ] kubectl 1.28+
- [ ] Helm 3.13+
- [ ] kubectl-ai (optional but recommended)
- [ ] OpenAI API key (reuse from `chatbot/backend/.env`)

**Verification Commands:**
```bash
docker --version          # Should be 24.0+
minikube version          # Should be v1.32+
kubectl version --client  # Should be v1.28+
helm version              # Should be v3.13+
docker ai "test"          # Should respond (if Gordon enabled)
```

### 3. Start Planning
Once you approve the constitution, ask Claude Code to create the plan:

**Prompt:**
```
Create an architectural plan for Phase IV Kubernetes deployment following the constitution.
Reference PHASE_IV_INSTRUCTIONS.md and the constitution principles.
```

Claude Code will create `specs/kubernetes-deployment/plan.md` with:
- Detailed Dockerfile specifications
- Helm chart template breakdown
- Environment variable mappings
- Service dependency graph
- Resource allocation strategy

---

## AI Tools Usage

### Gordon (Docker AI)
```bash
# Example usage
docker ai "Build a production Dockerfile for FastAPI app in todo-application/backend"
docker ai "Why is my container failing to start?"
docker ai "Optimize this image size"
```

### kubectl-ai
```bash
# Set OpenAI key (reuse from chatbot)
export OPENAI_API_KEY="sk-your-key-from-chatbot-env"

# Natural language commands
kubectl-ai "show me all pods and their status"
kubectl-ai "scale the todo-backend to 3 replicas"
kubectl-ai "why is my pod crashing?"
kubectl-ai "get the URLs for all services"
```

### kagent (Optional)
```bash
kagent "analyze cluster health"
kagent "optimize resource allocation"
kagent "why are my services not communicating?"
```

### Claude Code (Mandatory)
**Primary tool for:**
- Generating Dockerfiles
- Creating Helm charts
- Writing Kubernetes manifests
- Documenting deployment process

**NOT for:** Manual kubectl commands (use kubectl-ai) or manual coding

---

## Success Criteria

Phase IV is complete when:
- [ ] All 5 services deployed to Minikube (2 frontends, 2 backends, 1 database)
- [ ] Helm chart successfully installs/upgrades/rollsback application
- [ ] All quality gates passed
- [ ] Todo app accessible at `http://<minikube-ip>:30000`
- [ ] Chatbot accessible at `http://<minikube-ip>:30001`
- [ ] Core functionality verified (create/list/delete tasks via UI and chatbot)
- [ ] Documentation complete and accurate

---

## Next Steps

### Immediate Actions
1. **Review Constitution** - Read `.specify/memory/constitution.md`
2. **Approve or Amend** - Provide feedback on principles
3. **Check Prerequisites** - Install missing tools
4. **Start Planning** - Prompt Claude Code to create plan

### After Planning
1. **Review Plan** - Approve architecture decisions
2. **Implement Tasks** - Execute one task at a time via Claude Code
3. **Validate Gates** - Ensure each quality gate passes
4. **Deploy & Test** - Verify application works end-to-end
5. **Document** - Update README with deployment outcomes

---

## Resources

### Official Documentation
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes](https://kubernetes.io/docs/)
- [Helm](https://helm.sh/docs/)
- [kubectl-ai](https://github.com/sozercan/kubectl-ai)

### Project Files
- [PHASE_IV_INSTRUCTIONS.md](../PHASE_IV_INSTRUCTIONS.md) - Complete deployment guide
- [Constitution](./.specify/memory/constitution.md) - Principles and governance
- [CLAUDE.md](./CLAUDE.md) - AI agent workflow

### Learning Resources
- [12-Factor App](https://12factor.net/) - Cloud-native principles
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

---

## Troubleshooting

### Common Issues

**Image Pull Errors:**
```bash
# Ensure using Minikube's Docker daemon
eval $(minikube docker-env)
# Rebuild images
docker build -t todo-backend:v1 todo-application/backend/
```

**Pods Not Starting:**
```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Or use AI
kubectl-ai "why is my pod not starting?"
```

**Service Not Accessible:**
```bash
# Check services and endpoints
kubectl get services
kubectl get endpoints

# Use Minikube service helper
minikube service todo-frontend
```

**Database Connection Issues:**
```bash
# Verify PostgreSQL pod running
kubectl get pods | grep postgres

# Check environment variables
kubectl exec -it <backend-pod> -- env | grep DATABASE
```

For detailed troubleshooting, see [PHASE_IV_INSTRUCTIONS.md](../PHASE_IV_INSTRUCTIONS.md#troubleshooting).

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-30 | Initial constitution and project structure |

---

**Status**: Specification Complete - Ready for Planning
**Next**: User approval of constitution → Create architectural plan
