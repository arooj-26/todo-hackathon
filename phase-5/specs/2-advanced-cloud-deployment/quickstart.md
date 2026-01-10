# Phase V: Advanced Cloud Deployment - Quickstart Guide

This guide helps you set up, run, and deploy the Todo Chatbot application with advanced features (recurring tasks, reminders, event-driven architecture).

## Prerequisites

### Required Tools

| Tool | Version | Installation | Verification |
|------|---------|--------------|--------------|
| **Docker** | 24.0+ | [Install Docker](https://docs.docker.com/get-docker/) | `docker --version` |
| **Minikube** | 1.32+ | [Install Minikube](https://minikube.sigs.k8s.io/docs/start/) | `minikube version` |
| **kubectl** | 1.28+ | [Install kubectl](https://kubernetes.io/docs/tasks/tools/) | `kubectl version --client` |
| **Helm** | 3.13+ | [Install Helm](https://helm.sh/docs/intro/install/) | `helm version` |
| **Dapr CLI** | 1.12+ | [Install Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/) | `dapr --version` |
| **Python** | 3.11+ | [Install Python](https://www.python.org/downloads/) | `python --version` |
| **Node.js** | 20.0+ | [Install Node.js](https://nodejs.org/) | `node --version` |
| **Git** | 2.40+ | [Install Git](https://git-scm.com/downloads) | `git --version` |

### System Requirements

- **CPU**: 4+ cores (Minikube requires 2 cores minimum)
- **RAM**: 8GB+ (Minikube requires 4GB minimum)
- **Disk**: 20GB+ free space
- **OS**: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd web-todo/phase-5
```

### 2. Set Up Database (Neon PostgreSQL)

For local development, you have two options:

#### Option A: Use Neon Serverless PostgreSQL (Recommended)

1. Create a free account at [neon.tech](https://neon.tech)
2. Create a new project named "todo-chatbot-dev"
3. Copy the connection string
4. Create `.env` file:

```bash
# .env
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
JWT_SECRET=your-secret-key-change-in-production
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

#### Option B: Use Local PostgreSQL

```bash
# Using Docker
docker run -d \
  --name todo-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=todo_chatbot \
  -p 5432:5432 \
  postgres:16-alpine

# .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_chatbot
```

### 3. Initialize Dapr for Local Development

```bash
# Initialize Dapr
dapr init

# Verify Dapr installation
dapr --version
docker ps  # Should show dapr_redis, dapr_placement, dapr_zipkin
```

### 4. Start Kafka Locally

```bash
# Using Docker Compose
cat > docker-compose.kafka.yml <<EOF
version: '3.8'
services:
  kafka:
    image: bitnami/kafka:3.6
    ports:
      - "9092:9092"
    environment:
      KAFKA_CFG_NODE_ID: 1
      KAFKA_CFG_PROCESS_ROLES: controller,broker
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
    volumes:
      - kafka_data:/bitnami/kafka
volumes:
  kafka_data:
EOF

docker-compose -f docker-compose.kafka.yml up -d
```

### 5. Set Up Python Services

```bash
cd services

# Install dependencies for all services
for service in chat-api recurring-tasks notifications audit; do
  cd $service
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  cd ..
done
```

### 6. Set Up Frontend

```bash
cd frontend
npm install
```

### 7. Run Database Migrations

```bash
cd services/chat-api
source venv/bin/activate

# Run Alembic migrations
alembic upgrade head
```

## Running Services Locally

### Option 1: Run Services with Dapr (Recommended)

Each service runs with its Dapr sidecar for Pub/Sub, State Management, and Service Invocation.

#### Terminal 1: Chat API

```bash
cd services/chat-api
source venv/bin/activate

dapr run \
  --app-id chat-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../../k8s/dapr-components \
  -- uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Recurring Tasks Service

```bash
cd services/recurring-tasks
source venv/bin/activate

dapr run \
  --app-id recurring-tasks \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --dapr-grpc-port 50002 \
  --components-path ../../k8s/dapr-components \
  -- uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 3: Notifications Service

```bash
cd services/notifications
source venv/bin/activate

dapr run \
  --app-id notifications \
  --app-port 8002 \
  --dapr-http-port 3502 \
  --dapr-grpc-port 50003 \
  --components-path ../../k8s/dapr-components \
  -- uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

#### Terminal 4: Audit Service

```bash
cd services/audit
source venv/bin/activate

dapr run \
  --app-id audit \
  --app-port 8003 \
  --dapr-http-port 3503 \
  --dapr-grpc-port 50004 \
  --components-path ../../k8s/dapr-components \
  -- uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

#### Terminal 5: Frontend

```bash
cd frontend
npm run dev
```

#### Verify Services

```bash
# Check service health
curl http://localhost:8000/health  # Chat API
curl http://localhost:8001/health  # Recurring Tasks
curl http://localhost:8002/health  # Notifications
curl http://localhost:8003/health  # Audit

# Check frontend
open http://localhost:3000
```

### Option 2: Run Without Dapr (Development Only)

For quick testing without event-driven features:

```bash
# Terminal 1: Chat API
cd services/chat-api && uvicorn main:app --port 8000 --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

⚠️ **Note**: Without Dapr, event publishing and reminders won't work.

## Deploy to Minikube

### Quick Start: Automated Deployment (Recommended)

The fastest way to deploy to Minikube is using our automated deployment script:

```bash
cd ../k8s/scripts

# Make scripts executable (if needed)
chmod +x deploy-minikube.sh validate-deployment.sh

# Run automated deployment
./deploy-minikube.sh

# Validate deployment (after deployment completes)
./validate-deployment.sh
```

The automated script will:
- ✅ Check prerequisites (Minikube, kubectl, Helm, Dapr)
- ✅ Start Minikube with correct resources (4 CPU, 8GB RAM)
- ✅ Enable Minikube addons (ingress, metrics-server)
- ✅ Install Dapr control plane (v1.12)
- ✅ Deploy Strimzi Kafka operator and cluster
- ✅ Create Kafka topics (task-events, reminders, task-updates)
- ✅ Build all Docker images (using Minikube's Docker daemon)
- ✅ Deploy application with Helm
- ✅ Display access URLs and status

**Expected output:**
```
[SUCCESS] All prerequisites are installed
[SUCCESS] Minikube is already running
[SUCCESS] Minikube addons enabled
[SUCCESS] Dapr installed successfully
[SUCCESS] Strimzi Kafka Operator installed
[SUCCESS] Kafka cluster deployed
[SUCCESS] Kafka topics created
[SUCCESS] Docker images built
[SUCCESS] Todo App deployed successfully

======================================
Deployment completed successfully!
======================================

Access the application at: http://<minikube-ip>:30000

To view logs, use:
  kubectl logs -f deployment/todo-app-chat-api -n default

To run validation script:
  ./validate-deployment.sh
```

### Manual Deployment (Alternative)

If you prefer step-by-step deployment or need to customize:

#### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable addons
minikube addons enable metrics-server
minikube addons enable ingress

# Verify cluster
kubectl get nodes
```

#### 2. Install Dapr on Minikube

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr control plane
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait \
  --timeout 10m

# Verify Dapr installation
kubectl get pods -n dapr-system
```

#### 3. Install Kafka on Minikube (Strimzi)

```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
kubectl wait --for=condition=available --timeout=300s deployment/strimzi-cluster-operator -n kafka

# Deploy Kafka cluster
kubectl apply -f ../kafka/kafka-cluster.yaml -n kafka

# Wait for Kafka to be ready (takes 3-5 minutes)
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka

# Create Kafka topics
kubectl apply -f ../kafka/kafka-topics.yaml -n kafka
```

#### 4. Deploy PostgreSQL

```bash
# Create namespace
kubectl create namespace todo-app

# Deploy PostgreSQL
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: todoapp
        - name: POSTGRES_USER
          value: todoapp
        - name: POSTGRES_PASSWORD
          value: todoapp-dev-password
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: todo-app
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
EOF
```

#### 5. Build Docker Images

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Navigate to project root
cd ../../

# Build all images
docker build -t todo-app/chat-api:latest -f services/chat-api/Dockerfile services/chat-api/
docker build -t todo-app/recurring-tasks:latest -f services/recurring-tasks/Dockerfile services/recurring-tasks/
docker build -t todo-app/notifications:latest -f services/notifications/Dockerfile services/notifications/
docker build -t todo-app/audit:latest -f services/audit/Dockerfile services/audit/
docker build -t todo-app/frontend:latest -f services/frontend/Dockerfile services/frontend/
```

#### 6. Deploy Application with Helm

```bash
cd k8s/helm-charts/todo-app

# Install Helm chart with Minikube values
helm upgrade --install todo-app . \
  --namespace todo-app \
  --values values-minikube.yaml \
  --wait \
  --timeout 10m

# Verify deployment
kubectl get pods -n todo-app
```

#### 7. Access Application

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Access via NodePort
echo "Frontend:  http://$MINIKUBE_IP:30000"
echo "Chat API:  http://$MINIKUBE_IP:30080"

# Or use port forwarding
kubectl port-forward -n todo-app svc/frontend 3000:3000
kubectl port-forward -n todo-app svc/chat-api 8000:8000
```

### Validate Deployment

Run the validation script to verify all components are healthy:

```bash
cd k8s/scripts
./validate-deployment.sh
```

The script checks:
- ✅ Dapr system pods
- ✅ Kafka cluster and topics
- ✅ PostgreSQL database
- ✅ All application services
- ✅ Health endpoints
- ✅ Dapr components

### Verify Event-Driven Features

```bash
# Check Dapr sidecars are running
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# View Kafka topics
kubectl exec -it -n kafka kafka-cluster-kafka-0 -- bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Consume events from task-events topic (for testing)
kubectl exec -it -n kafka kafka-cluster-kafka-0 -- bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning

# Access Dapr dashboard
dapr dashboard -k -n todo-app
```

## Running Tests

### Unit Tests

```bash
cd services/chat-api
source venv/bin/activate
pytest tests/unit/ -v --cov=app --cov-report=html

cd ../recurring-tasks
pytest tests/unit/ -v

cd ../notifications
pytest tests/unit/ -v
```

### Integration Tests

```bash
cd services/chat-api
pytest tests/integration/ -v --log-cli-level=INFO
```

### End-to-End Tests

```bash
cd tests/e2e
npm install
npm test
```

## Troubleshooting

### Issue: Dapr sidecar not injecting

**Symptoms**: Pods running but no events being published

**Solution**:
```bash
# Verify Dapr annotation on deployment
kubectl get deployment chat-api -n todo -o yaml | grep dapr.io

# Should see:
#   dapr.io/enabled: "true"
#   dapr.io/app-id: "chat-api"
#   dapr.io/app-port: "8000"

# Restart deployment if annotations missing
kubectl rollout restart deployment/chat-api -n todo
```

### Issue: Kafka connection refused

**Symptoms**: Dapr logs show "connection refused" to Kafka

**Solution**:
```bash
# Check Kafka is running
kubectl get kafka -n kafka

# Check Kafka bootstrap service
kubectl get svc -n kafka | grep bootstrap

# Update Dapr pubsub component with correct broker address
kubectl edit component pubsub -n todo
# Set brokers: ["todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"]
```

### Issue: Database connection timeout

**Symptoms**: Services can't connect to Neon PostgreSQL

**Solution**:
```bash
# Check secret is correct
kubectl get secret postgres-secret -n todo -o jsonpath='{.data.connectionString}' | base64 -d

# Test connection from pod
kubectl run -it --rm debug --image=postgres:16 --restart=Never -n todo -- \
  psql "$DATABASE_URL" -c "SELECT 1"

# Verify SSL mode is set to 'require' for Neon
```

### Issue: Minikube out of resources

**Symptoms**: Pods stuck in Pending state

**Solution**:
```bash
# Check node resources
kubectl describe nodes

# Increase Minikube resources
minikube stop
minikube delete
minikube start --cpus=6 --memory=12288
```

### Issue: Dapr component not found

**Symptoms**: Error "component pubsub not found"

**Solution**:
```bash
# List Dapr components
dapr components -k -n todo

# Re-apply components
kubectl apply -f k8s/dapr-components/ -n todo

# Restart affected pods
kubectl rollout restart deployment/chat-api -n todo
```

### Issue: Frontend can't reach backend

**Symptoms**: CORS errors or connection refused

**Solution**:
```bash
# Check service endpoints
kubectl get endpoints -n todo

# Port forward correct service
kubectl port-forward -n todo svc/chat-api 8000:8000

# Update frontend .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Monitoring and Logs

### View Service Logs

```bash
# Chat API logs
kubectl logs -f -n todo -l app=chat-api -c chat-api

# Dapr sidecar logs
kubectl logs -f -n todo -l app=chat-api -c daprd

# All logs from a pod
kubectl logs -f -n todo <pod-name> --all-containers
```

### Access Zipkin for Distributed Tracing

```bash
# Port forward Zipkin
kubectl port-forward -n dapr-system svc/dapr-zipkin 9411:9411

# Open Zipkin UI
open http://localhost:9411
```

### Access Dapr Dashboard

```bash
# Run Dapr dashboard
dapr dashboard -k -p 9999

# Open dashboard
open http://localhost:9999
```

## Next Steps

1. **Read Architecture Docs**: See `plan.md` for system architecture
2. **Review Data Model**: See `data-model.md` for database schema
3. **Explore API Contracts**: See `contracts/openapi.yaml` for API spec
4. **Deploy to Cloud**: Follow cloud deployment guide for AKS/GKE/OKE
5. **Set Up CI/CD**: Configure GitHub Actions for automated deployments

## Useful Commands Reference

```bash
# Minikube
minikube status                          # Check Minikube status
minikube dashboard                       # Open Kubernetes dashboard
minikube service list -n todo            # List services with URLs
minikube logs                            # View Minikube logs

# Kubectl
kubectl get all -n todo                  # List all resources
kubectl describe pod <pod-name> -n todo  # Get pod details
kubectl exec -it <pod-name> -n todo -- /bin/sh  # Shell into pod
kubectl delete pod <pod-name> -n todo    # Delete and recreate pod

# Helm
helm list -n todo                        # List releases
helm status todo-app -n todo             # Release status
helm upgrade todo-app . -n todo          # Upgrade release
helm uninstall todo-app -n todo          # Uninstall release

# Dapr
dapr list -k -n todo                     # List Dapr apps
dapr logs -k -a chat-api -n todo         # View app logs
dapr invoke -k -a chat-api -n todo -m health  # Invoke service

# Docker
docker ps                                # List running containers
docker logs <container-id>               # View container logs
docker-compose logs -f                   # View compose logs
```

## Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Strimzi Kafka Documentation](https://strimzi.io/documentation/)
- [Helm Documentation](https://helm.sh/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
