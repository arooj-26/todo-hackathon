# Cloud Deployment Guide

This guide covers deploying the Todo Chatbot application to production cloud environments (Azure AKS, Google GKE, and Oracle OKE).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Azure AKS Deployment](#azure-aks-deployment)
- [Google GKE Deployment](#google-gke-deployment)
- [Oracle OKE Deployment](#oracle-oke-deployment)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **kubectl** | 1.28+ | Kubernetes CLI |
| **helm** | 3.13+ | Package manager for Kubernetes |
| **Docker** | 24.0+ | Container images |

### Cloud-Specific CLIs

| Cloud Provider | CLI Tool | Installation |
|----------------|----------|--------------|
| **Azure** | Azure CLI (`az`) | [Install](https://docs.microsoft.com/cli/azure/install-azure-cli) |
| **Google Cloud** | gcloud CLI | [Install](https://cloud.google.com/sdk/docs/install) |
| **Oracle Cloud** | OCI CLI (`oci`) | [Install](https://docs.oracle.com/iaas/Content/API/SDKDocs/cliinstall.htm) |

### Cloud Resources to Prepare

Before deployment, ensure you have:

1. **Managed Kubernetes cluster** (AKS/GKE/OKE) or permissions to create one
2. **Container registry** (ACR/GCR/OCIR) for Docker images
3. **Managed PostgreSQL database** (Azure Database/Cloud SQL/Autonomous DB)
4. **Domain name** for ingress routing
5. **SSL certificate** or cert-manager setup
6. **Cloud credentials** with appropriate permissions

## Architecture Overview

### Production Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Internet                          │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          NGINX Ingress Controller                   │
│              (LoadBalancer)                         │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────┐                   ┌───▼────┐
│Frontend│                   │Chat API│
│(3 pods)│                   │(3 pods)│
└───┬────┘                   └───┬────┘
    │                            │
    │         ┌──────────────────┼──────────────────┐
    │         │                  │                  │
┌───▼─────┐ ┌▼──────────┐ ┌────▼──────┐   ┌──────▼────┐
│Recurring│ │Notifications│ │Audit      │   │PostgreSQL │
│Tasks    │ │(3 pods)     │ │(3 pods)   │   │(Managed)  │
│(3 pods) │ └──────┬──────┘ └─────┬─────┘   └───────────┘
└────┬────┘        │              │
     │             │              │
     └─────────────┼──────────────┘
                   │
        ┌──────────▼──────────┐
        │   Kafka (Strimzi)   │
        │   or Managed Kafka  │
        └─────────────────────┘
```

### Key Components

- **Horizontal Pod Autoscaler (HPA)**: Auto-scales pods based on CPU/memory
- **PodDisruptionBudget (PDB)**: Ensures minimum availability during updates
- **Ingress**: Routes external traffic with TLS termination
- **Dapr sidecars**: Handle pub/sub, state management, and service invocation
- **Monitoring**: Prometheus metrics + Grafana dashboards

## Azure AKS Deployment

### Step 1: Set Environment Variables

```bash
export RESOURCE_GROUP="todo-app-rg"
export AKS_CLUSTER_NAME="todo-app-aks"
export ACR_NAME="todoappackr"  # Must be globally unique
export LOCATION="eastus"
export NODE_COUNT="3"
```

### Step 2: Run Deployment Script

```bash
cd k8s/scripts
./deploy-aks.sh
```

The script will:
- Create Azure resource group
- Create Azure Container Registry (ACR)
- Create AKS cluster with managed identity
- Install NGINX Ingress Controller
- Install cert-manager for TLS
- Install Dapr control plane
- Deploy Strimzi Kafka operator
- Build and push Docker images to ACR
- Deploy application with Helm

### Step 3: Create Managed Database

```bash
# Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name todo-app-db \
  --location $LOCATION \
  --admin-user todoadmin \
  --admin-password <strong-password> \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose \
  --storage-size 32 \
  --version 15

# Get connection string
DB_HOST=$(az postgres flexible-server show \
  --resource-group $RESOURCE_GROUP \
  --name todo-app-db \
  --query fullyQualifiedDomainName -o tsv)

DATABASE_URL="postgresql://todoadmin:<password>@${DB_HOST}:5432/todoapp?sslmode=require"
```

### Step 4: Create Database Secret

```bash
kubectl create secret generic postgres-secret \
  --from-literal=connection-string="$DATABASE_URL" \
  -n todo-app
```

### Step 5: Configure DNS

```bash
# Get ingress IP
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Configure DNS A records:"
echo "  todoapp.yourdomain.com -> $INGRESS_IP"
echo "  api.todoapp.yourdomain.com -> $INGRESS_IP"
```

### Step 6: Update and Redeploy with Domain

```bash
helm upgrade todo-app ../helm-charts/todo-app/ \
  --namespace todo-app \
  --values ../helm-charts/todo-app/values-cloud.yaml \
  --set global.imageRegistry="$ACR_NAME.azurecr.io" \
  --set ingress.hosts[0].host="todoapp.yourdomain.com" \
  --set ingress.hosts[1].host="api.todoapp.yourdomain.com" \
  --wait
```

## Google GKE Deployment

### Step 1: Set Environment Variables

```bash
export PROJECT_ID="your-gcp-project-id"
export CLUSTER_NAME="todo-app-gke"
export REGION="us-central1"
export ZONE="us-central1-a"
export NODE_COUNT="3"
```

### Step 2: Run Deployment Script

```bash
cd k8s/scripts
./deploy-gke.sh
```

The script will:
- Enable required GCP APIs
- Create GKE cluster with autoscaling
- Configure Docker for GCR
- Install NGINX Ingress, cert-manager, Dapr
- Deploy Kafka operator
- Build and push images to GCR
- Configure Workload Identity
- Deploy application with Helm

### Step 3: Create Cloud SQL Instance

```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create todo-app-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=$REGION \
  --network=default \
  --no-assign-ip

# Create database
gcloud sql databases create todoapp \
  --instance=todo-app-db

# Create user
gcloud sql users create todoadmin \
  --instance=todo-app-db \
  --password=<strong-password>

# Get connection name
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe todo-app-db \
  --format='value(connectionName)')

# For Cloud SQL Proxy
DATABASE_URL="postgresql://todoadmin:<password>@localhost:5432/todoapp"
```

### Step 4: Configure Cloud SQL Proxy

```bash
# Deploy Cloud SQL Proxy as sidecar in Helm values
# Or use Workload Identity with Cloud SQL Auth Proxy
```

### Step 5: Configure DNS (same as AKS)

```bash
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Configure DNS A records
```

## Oracle OKE Deployment

### Step 1: Set Environment Variables

```bash
export COMPARTMENT_ID="ocid1.compartment.oc1..xxx"
export CLUSTER_NAME="todo-app-oke"
export REGION="us-ashburn-1"
export NODE_COUNT="3"
export OCI_AUTH_TOKEN="<your-auth-token>"  # Generate in OCI Console
```

### Step 2: Create OKE Cluster via Console (Recommended)

1. Navigate to OCI Console → Developer Services → Kubernetes Clusters (OKE)
2. Click "Create Cluster" → "Quick Create"
3. Configure:
   - Name: `todo-app-oke`
   - Kubernetes version: Latest
   - Node pool shape: VM.Standard.E3.Flex
   - Number of nodes: 3
4. Click "Create Cluster" and wait for completion

### Step 3: Run Deployment Script

```bash
cd k8s/scripts
./deploy-oke.sh
```

### Step 4: Create Autonomous Database

```bash
# Create via OCI Console or CLI
oci db autonomous-database create \
  --compartment-id $COMPARTMENT_ID \
  --db-name todoappdb \
  --display-name "Todo App DB" \
  --admin-password <strong-password> \
  --cpu-core-count 1 \
  --data-storage-size-in-tbs 1

# Download wallet for connection
# Set DATABASE_URL with wallet path
```

## Post-Deployment Configuration

### 1. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# View Helm release
helm list -n todo-app
```

### 2. Run Validation Script

```bash
cd k8s/scripts
./validate-deployment.sh
```

### 3. Configure Monitoring

```bash
# Install Prometheus and Grafana (if not already)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Default credentials: admin/prom-operator
```

### 4. Set Up Alerts

Configure alerting in Prometheus for:
- Pod failures
- High CPU/memory usage
- Database connection failures
- Kafka lag
- API error rates

### 5. Enable Backups

- **Database**: Configure automated backups (daily recommended)
- **Kafka**: Configure topic retention and replication
- **Application state**: Backup Dapr state store

## Rollback Procedures

### Quick Rollback to Previous Version

```bash
cd k8s/scripts
./rollback.sh
```

### Rollback to Specific Revision

```bash
# View revision history
helm history todo-app -n todo-app

# Rollback to revision 3
./rollback.sh -r 3
```

### Manual Rollback

```bash
# Rollback Helm release
helm rollback todo-app 3 -n todo-app

# Verify rollback
kubectl get pods -n todo-app
helm status todo-app -n todo-app
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check service health endpoints
curl https://api.todoapp.yourdomain.com/health

# View pod status
kubectl get pods -n todo-app -w

# Check Dapr status
dapr status -k -n todo-app
```

### View Logs

```bash
# View application logs
kubectl logs -n todo-app -l app=chat-api -c chat-api --tail=100 -f

# View Dapr sidecar logs
kubectl logs -n todo-app -l app=chat-api -c daprd --tail=100 -f

# View all logs from a pod
kubectl logs -n todo-app <pod-name> --all-containers -f
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment chat-api -n todo-app --replicas=5

# View HPA status
kubectl get hpa -n todo-app

# Adjust HPA limits
kubectl patch hpa chat-api-hpa -n todo-app \
  -p '{"spec":{"maxReplicas":15}}'
```

### Updates and Upgrades

```bash
# Update application
helm upgrade todo-app ../helm-charts/todo-app/ \
  --namespace todo-app \
  --values ../helm-charts/todo-app/values-cloud.yaml \
  --set chatApi.image.tag="v1.2.0" \
  --wait

# Update Dapr
helm upgrade dapr dapr/dapr \
  --namespace dapr-system \
  --wait

# Update Kafka operator
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
```

## Troubleshooting

### Pod Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check image pull
kubectl get pods <pod-name> -n todo-app -o jsonpath='{.status.containerStatuses[*].state}'
```

### Database Connection Issues

```bash
# Test database connectivity from pod
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n todo-app -- \
  psql "$DATABASE_URL" -c "SELECT 1"

# Check secret
kubectl get secret postgres-secret -n todo-app -o yaml

# Verify SSL mode for cloud databases
```

### Kafka Issues

```bash
# Check Kafka cluster status
kubectl get kafka -n kafka

# View Kafka broker logs
kubectl logs -n kafka kafka-cluster-kafka-0

# Test Kafka connectivity
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# View ingress configuration
kubectl describe ingress todo-app-ingress -n todo-app

# Check cert-manager certificates
kubectl get certificates -n todo-app
kubectl describe certificate todoapp-tls -n todo-app
```

### High Resource Usage

```bash
# View resource usage
kubectl top pods -n todo-app

# Check HPA metrics
kubectl get hpa -n todo-app -o yaml

# View resource limits
kubectl describe pod <pod-name> -n todo-app | grep -A 5 "Limits"
```

## Best Practices

1. **Use semantic versioning** for Docker images (not `latest`)
2. **Enable autoscaling** with appropriate min/max replicas
3. **Configure resource requests and limits** for all pods
4. **Use external secret management** (Azure Key Vault, GCP Secret Manager, OCI Vault)
5. **Enable network policies** to restrict inter-pod communication
6. **Implement circuit breakers** and retries in Dapr
7. **Regular backups** of database and Kafka topics
8. **Monitor and alert** on key metrics
9. **Test rollback procedures** regularly
10. **Use blue-green or canary deployments** for critical updates

## Security Considerations

- Use **managed identities** for cloud service access
- Enable **Pod Security Policies** or **Pod Security Standards**
- Use **network policies** to restrict traffic
- **Scan container images** for vulnerabilities
- **Rotate secrets** regularly
- Use **TLS** for all external and internal communication
- Enable **audit logging** for Kubernetes API
- Implement **RBAC** with least privilege

## Cost Optimization

- Use **node autoscaling** to scale down during low traffic
- Use **spot/preemptible instances** for non-critical workloads
- Configure **HPA** with appropriate thresholds
- Use **managed services** where cost-effective (managed Kafka, databases)
- Monitor and optimize **resource requests/limits**
- Use **reserved instances** for production workloads

## Support and Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Strimzi Documentation](https://strimzi.io/documentation/)
- Azure: [AKS Documentation](https://docs.microsoft.com/azure/aks/)
- Google Cloud: [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- Oracle: [OKE Documentation](https://docs.oracle.com/iaas/Content/ContEng/home.htm)
