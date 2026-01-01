# Todo App Helm Chart

Kubernetes Helm chart for deploying the Todo Application with AI Chatbot.

## Overview

This Helm chart deploys a complete todo application stack with:
- **Todo Frontend** (Next.js) - User interface for managing tasks
- **Todo Backend** (FastAPI/Python) - REST API for todo operations
- **Chatbot Frontend** (Next.js) - Chat interface for AI assistant
- **Chatbot Backend** (FastAPI/Python) - AI-powered chatbot service
- **PostgreSQL** - Persistent database storage

## Prerequisites

- Docker 4.53+ or compatible container runtime
- Minikube 1.32+ or Kubernetes 1.28+
- kubectl 1.28+
- Helm 3.13+ (optional if using rendered manifests)
- 4 CPU cores and 8GB RAM minimum for Minikube

## Quick Start

### 1. Start Minikube

```bash
# Start Minikube cluster
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable metrics server
minikube addons enable metrics-server

# Verify cluster is running
minikube status
```

### 2. Build Docker Images

Configure Docker to use Minikube's daemon:

```bash
# Set Docker environment (run in each new terminal)
eval $(minikube docker-env)

# Build all images
docker build -t todo-backend:v1 ../../todo-application/backend/
docker build -t todo-frontend:v1 ../../todo-application/frontend/
docker build -t chatbot-backend:v1 ../../chatbot/backend/
docker build -t chatbot-frontend:v1 ../../chatbot/frontend/

# Verify images are in Minikube
minikube ssh "docker images | grep -E 'todo|chatbot'"
```

### 3. Configure Secrets

Edit `values.yaml` and update the secrets section:

```yaml
secrets:
  postgresPassword: "your-secure-password"
  secretKey: "your-jwt-secret-key"
  openaiApiKey: "your-openai-api-key"
```

**⚠️ IMPORTANT**: Never commit `values.yaml` with real secrets to Git!

### 4. Deploy Application

#### Option A: Using Helm (Recommended)

```bash
# Install the chart
helm install todo-app .

# Or upgrade if already installed
helm upgrade todo-app .
```

#### Option B: Using Rendered Manifests

```bash
# Apply the rendered Kubernetes manifests
kubectl apply -f ../../rendered/
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get services

# Check deployments
kubectl get deployments

# View pod logs
kubectl logs -l app=todo-backend --tail=20
kubectl logs -l app=chatbot-backend --tail=20
```

### 6. Access Applications

Get the Minikube IP:

```bash
minikube ip
```

Access the applications in your browser:

- **Todo Frontend**: `http://<minikube-ip>:30000`
- **Chatbot Frontend**: `http://<minikube-ip>:30001`

Or use Minikube service command to open automatically:

```bash
minikube service todo-frontend
minikube service chatbot-frontend
```

## Configuration

### Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name | `development` |
| `images.*.repository` | Image repository | `todo-backend`, `todo-frontend`, etc. |
| `images.*.tag` | Image tag | `v1` |
| `images.*.pullPolicy` | Image pull policy | `Never` (for local images) |
| `replicas.todoFrontend` | Number of todo frontend replicas | `2` |
| `replicas.todoBackend` | Number of todo backend replicas | `1` |
| `replicas.chatbotFrontend` | Number of chatbot frontend replicas | `2` |
| `replicas.chatbotBackend` | Number of chatbot backend replicas | `1` |
| `replicas.postgres` | Number of postgres replicas | `1` |
| `services.todoFrontend.nodePort` | NodePort for todo frontend | `30000` |
| `services.chatbotFrontend.nodePort` | NodePort for chatbot frontend | `30001` |
| `storage.postgres.size` | PostgreSQL PVC size | `5Gi` |
| `secrets.postgresPassword` | PostgreSQL password | (set before deployment) |
| `secrets.secretKey` | JWT secret key | (set before deployment) |
| `secrets.openaiApiKey` | OpenAI API key | (set before deployment) |

### Resource Limits

Default resource allocation per service:

| Service | CPU Request | Memory Request | CPU Limit | Memory Limit |
|---------|-------------|----------------|-----------|--------------|
| Todo Frontend | 200m | 256Mi | 500m | 512Mi |
| Todo Backend | 250m | 256Mi | 500m | 512Mi |
| Chatbot Frontend | 200m | 256Mi | 500m | 512Mi |
| Chatbot Backend | 250m | 256Mi | 500m | 512Mi |
| PostgreSQL | 250m | 512Mi | 500m | 1024Mi |

**Total Required**: ~1350m CPU, ~1792Mi RAM (minimum)

## Operations

### Scaling

Scale deployments using kubectl or Helm:

```bash
# Scale todo-backend to 2 replicas
kubectl scale deployment todo-backend --replicas=2

# Or update values.yaml and upgrade with Helm
helm upgrade todo-app .
```

### Viewing Logs

```bash
# All logs for an app
kubectl logs -l app=todo-backend

# Follow logs in real-time
kubectl logs -l app=todo-backend -f

# Logs from specific pod
kubectl logs <pod-name>

# Last 50 lines
kubectl logs -l app=chatbot-backend --tail=50
```

### Exec into Pods

```bash
# Execute commands in a pod
kubectl exec -it <pod-name> -- /bin/bash

# Check database
kubectl exec -it $(kubectl get pod -l app=postgresql -o name | head -1) -- psql -U postgres
```

### Health Checks

All services expose `/health` endpoints:

```bash
# Check backend health
kubectl exec -it $(kubectl get pod -l app=todo-frontend -o name | head -1) -- \
  curl http://todo-backend:8000/health

kubectl exec -it $(kubectl get pod -l app=chatbot-frontend -o name | head -1) -- \
  curl http://chatbot-backend:8001/health
```

### Rollback

```bash
# View deployment history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app <revision-number>
```

### Uninstall

```bash
# Using Helm
helm uninstall todo-app

# Using kubectl
kubectl delete -f ../../rendered/

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│ Todo Frontend   │────────▶│  Todo Backend    │
│ (Next.js:3000)  │         │  (FastAPI:8000)  │
│ NodePort:30000  │         │  ClusterIP       │
└─────────────────┘         └─────────┬────────┘
                                      │
┌─────────────────┐         ┌────────▼─────────┐
│ Chatbot Frontend│────────▶│ Chatbot Backend  │
│ (Next.js:3001)  │         │ (FastAPI:8001)   │
│ NodePort:30001  │         │  ClusterIP       │
└─────────────────┘         └─────────┬────────┘
                                      │
                            ┌─────────▼────────┐
                            │   PostgreSQL     │
                            │   (Port:5432)    │
                            │   ClusterIP      │
                            │   + 5Gi PVC      │
                            └──────────────────┘
```

## Development

### Updating the Chart

1. Modify templates in `templates/`
2. Update `values.yaml` if adding new configuration
3. Test with dry-run: `helm install --dry-run --debug todo-app .`
4. Lint the chart: `helm lint .`
5. Apply changes: `helm upgrade todo-app .`

### Adding New Services

1. Create deployment YAML in `templates/<service>-deployment.yaml`
2. Create service YAML in `templates/<service>-service.yaml`
3. Add image configuration to `values.yaml`
4. Update `_helpers.tpl` if needed
5. Test deployment

## Support

For issues and questions:
- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Review pod logs: `kubectl logs <pod-name>`
- Check events: `kubectl get events --sort-by='.lastTimestamp'`
- Describe resources: `kubectl describe pod <pod-name>`

## License

See main project README for license information.
