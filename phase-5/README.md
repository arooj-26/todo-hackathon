# Todo Chatbot - Phase V: Advanced Cloud Deployment

Event-driven microservices architecture with recurring tasks, automated reminders, and production-grade cloud deployment.

## 🏗️ Architecture Overview

This project implements a scalable, event-driven microservices architecture deployed to Kubernetes with full observability and CI/CD automation.

### Microservices

- **Chat API** (Port 8000): User-facing REST API, task CRUD, event publishing
- **Recurring Task Service** (Port 8001): Consumes task completion events, generates next recurring instances
- **Notification Service** (Port 8002): Reminder scheduling via Dapr Jobs API, notification dispatch
- **Audit Service** (Port 8003): Event consumption for audit log and compliance reporting
- **Frontend** (Port 3000): Next.js 14 web application with real-time updates

### Technology Stack

**Backend:**
- Python 3.11, FastAPI 0.104+, SQLModel
- PostgreSQL (Neon Serverless) for persistent storage
- Kafka (Strimzi or Redpanda Cloud) for event streaming

**Frontend:**
- Next.js 14, TypeScript, TanStack Query, Zustand, Tailwind CSS

**Infrastructure:**
- Dapr 1.12+ for infrastructure abstraction (Pub/Sub, State, Jobs, Secrets APIs)
- Kubernetes 1.28+ (Minikube local, AKS/GKE/OKE cloud)
- Helm 3.13+ for deployment management
- Prometheus, Grafana, Zipkin for observability

### Event-Driven Architecture

**Kafka Topics:**
- `task-events`: TaskEvent (create, update, complete, delete)
- `reminders`: ReminderEvent (reminder due, sent, failed)
- `task-updates`: TaskUpdateEvent (real-time UI synchronization)

All services communicate through events for decoupled, scalable processing.

## 🚀 Quick Start

### Prerequisites

- Docker 24.0+
- Minikube 1.32+ (for local Kubernetes)
- kubectl 1.28+
- Helm 3.13+
- Dapr CLI 1.12+
- Python 3.11+
- Node.js 20+

### Local Development with Docker Compose

```bash
# Start all services with Kafka, PostgreSQL, and Dapr sidecars
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Chat API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Deploy to Minikube

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Install Dapr on Kubernetes
dapr init -k

# Install Strimzi Kafka operator
kubectl create namespace kafka
kubectl apply -f k8s/kafka/strimzi-operator.yaml -n kafka

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Deploy application with Helm
helm install todo-app k8s/helm-charts/todo-app/ \
  --namespace todo \
  --create-namespace \
  --values k8s/helm-charts/todo-app/values-minikube.yaml

# Verify deployment
kubectl get pods -n todo
```

For detailed instructions, see [Quickstart Guide](specs/2-advanced-cloud-deployment/quickstart.md).

## 📋 Features

### Phase V Advanced Features (P1)

- ✅ **Recurring Tasks**: Automatic next instance creation on completion
- ✅ **Due Dates & Reminders**: Scheduled notifications before deadlines
- ✅ **Event-Driven Architecture**: All operations publish to Kafka
- ✅ **Progressive Deployment**: Minikube → Cloud staging → Production

### Phase V Intermediate Features (P2)

- ✅ **Priorities & Tags**: Task organization with high/medium/low priority and custom tags
- ✅ **Advanced Search**: Full-text search with multi-criteria filtering
- ✅ **Sorting**: Multi-criteria sort (priority, due date, created date, title)
- ✅ **CI/CD Pipeline**: Automated builds, tests, and deployments with GitHub Actions
- ✅ **Monitoring & Observability**: Prometheus metrics, Grafana dashboards, Zipkin tracing

## 📁 Project Structure

```
phase-5/
├── services/                    # Microservices
│   ├── chat-api/               # Chat API + MCP Tools (FastAPI)
│   │   ├── src/
│   │   │   ├── api/            # REST endpoints
│   │   │   ├── models/         # SQLModel entities
│   │   │   ├── services/       # Business logic
│   │   │   ├── events/         # Event schemas
│   │   │   └── dapr/           # Dapr client wrappers
│   │   ├── migrations/         # Alembic database migrations
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── recurring-tasks/        # Recurring Task Service
│   ├── notifications/          # Notification Service
│   ├── audit/                  # Audit Service
│   └── frontend/               # Next.js 14 frontend
│       ├── src/
│       │   ├── app/            # App Router pages
│       │   ├── components/     # React components
│       │   ├── hooks/          # TanStack Query hooks
│       │   └── lib/            # API client, store
│       ├── package.json
│       └── Dockerfile
├── k8s/                        # Kubernetes manifests
│   ├── helm-charts/
│   │   └── todo-app/           # Helm chart for all services
│   │       ├── templates/
│   │       │   ├── deployments/
│   │       │   ├── services/
│   │       │   ├── dapr-components/
│   │       │   └── ingress/
│   │       ├── values.yaml
│   │       ├── values-minikube.yaml
│   │       └── values-cloud.yaml
│   └── kafka/                  # Strimzi Kafka manifests
├── specs/                      # Design documents
│   └── 2-advanced-cloud-deployment/
│       ├── spec.md             # Feature specification
│       ├── plan.md             # Implementation plan
│       ├── data-model.md       # Database schema
│       ├── tasks.md            # Task breakdown (180 tasks)
│       ├── quickstart.md       # Developer guide
│       └── contracts/          # API contracts
├── docker-compose.yml          # Local development
└── README.md                   # This file
```

## 🧪 Testing

```bash
# Backend unit tests
cd services/chat-api
pytest tests/unit/

# Backend integration tests
pytest tests/integration/

# Frontend tests
cd services/frontend
npm test
```

## 📚 Documentation

- **[Feature Specification](specs/2-advanced-cloud-deployment/spec.md)**: User stories and requirements
- **[Implementation Plan](specs/2-advanced-cloud-deployment/plan.md)**: Technical architecture and decisions
- **[Data Model](specs/2-advanced-cloud-deployment/data-model.md)**: Database schema and relationships
- **[Task Breakdown](specs/2-advanced-cloud-deployment/tasks.md)**: 180 implementation tasks
- **[Quickstart Guide](specs/2-advanced-cloud-deployment/quickstart.md)**: Detailed setup instructions
- **[API Contracts](specs/2-advanced-cloud-deployment/contracts/openapi.yaml)**: REST API specification

## 🔗 Links

- **Constitution**: [.specify/memory/constitution.md](../.specify/memory/constitution.md)
- **GitHub Repository**: [web-todo](https://github.com/your-org/web-todo)
- **Documentation**: [Phase V Specs](specs/2-advanced-cloud-deployment/)

## 📈 Implementation Progress

- ✅ Phase 1: Setup (13/13 tasks complete)
- ⏳ Phase 2: Foundational (0/29 tasks)
- ⏳ Phase 3: US1 Recurring Tasks (0/20 tasks)
- ⏳ Phase 4: US2 Reminders (0/19 tasks)

**Total Progress**: 13/180 tasks (7%)

## 🤝 Contributing

This project follows the Agentic Dev Stack workflow:
1. Write spec → 2. Generate plan → 3. Break into tasks → 4. Implement via Claude Code

See [CLAUDE.md](CLAUDE.md) for development guidelines.

## 📝 License

MIT License - See LICENSE file for details

---

**Phase V MVP**: Recurring Tasks + Automated Reminders + Cloud Deployment + Monitoring

Built with ❤️ using the Agentic Dev Stack
