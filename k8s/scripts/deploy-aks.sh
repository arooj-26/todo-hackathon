#!/bin/bash
# Azure Kubernetes Service (AKS) deployment script for Todo App
# This script deploys the complete system to Azure AKS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-todo-app-rg}"
CLUSTER_NAME="${CLUSTER_NAME:-todo-app-aks}"
LOCATION="${LOCATION:-eastus}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_VM_SIZE="${NODE_VM_SIZE:-Standard_D2s_v3}"
ACR_NAME="${ACR_NAME:-todoappackr}"
NAMESPACE="${NAMESPACE:-todo-app}"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
CHART_PATH="../helm-charts/todo-app"
VALUES_FILE="../helm-charts/todo-app/values-cloud.yaml"

# Check prerequisites
print_status "Checking prerequisites..."
for cmd in az kubectl helm; do
    if ! command -v $cmd &> /dev/null; then
        print_error "$cmd is not installed"
        exit 1
    fi
done
print_success "All prerequisites installed"

# Login to Azure
print_status "Checking Azure login..."
if ! az account show &> /dev/null; then
    print_status "Logging in to Azure..."
    az login
fi
print_success "Logged in to Azure"

# Create resource group
print_status "Creating resource group..."
az group create --name ${RESOURCE_GROUP} --location ${LOCATION} || print_warning "Resource group might already exist"
print_success "Resource group ready"

# Create ACR
print_status "Creating Azure Container Registry..."
az acr create --resource-group ${RESOURCE_GROUP} --name ${ACR_NAME} --sku Standard || print_warning "ACR might already exist"
print_success "ACR ready"

# Create AKS cluster
print_status "Creating AKS cluster (this may take 10-15 minutes)..."
if ! az aks show --resource-group ${RESOURCE_GROUP} --name ${CLUSTER_NAME} &> /dev/null; then
    az aks create \
        --resource-group ${RESOURCE_GROUP} \
        --name ${CLUSTER_NAME} \
        --node-count ${NODE_COUNT} \
        --node-vm-size ${NODE_VM_SIZE} \
        --enable-addons monitoring \
        --generate-ssh-keys \
        --attach-acr ${ACR_NAME} \
        --enable-managed-identity
    print_success "AKS cluster created"
else
    print_success "AKS cluster already exists"
fi

# Get AKS credentials
print_status "Getting AKS credentials..."
az aks get-credentials --resource-group ${RESOURCE_GROUP} --name ${CLUSTER_NAME} --overwrite-existing
print_success "Credentials configured"

# Install NGINX Ingress Controller
print_status "Installing NGINX Ingress Controller..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
    --wait
print_success "NGINX Ingress Controller installed"

# Install cert-manager for TLS
print_status "Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
kubectl wait --for=condition=Available --timeout=300s deployment/cert-manager -n cert-manager
print_success "cert-manager installed"

# Install Dapr
print_status "Installing Dapr..."
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm upgrade --install dapr dapr/dapr \
    --namespace dapr-system \
    --create-namespace \
    --set global.ha.enabled=true \
    --wait
print_success "Dapr installed"

# Create namespace
print_status "Creating application namespace..."
kubectl create namespace ${NAMESPACE} || print_warning "Namespace might already exist"
print_success "Namespace ready"

# Build and push Docker images
print_status "Building and pushing Docker images to ACR..."
az acr login --name ${ACR_NAME}
ACR_LOGIN_SERVER=$(az acr show --name ${ACR_NAME} --query loginServer --output tsv)

for service in chat-api recurring-tasks notifications audit frontend; do
    print_status "Building ${service}..."
    docker build -t ${ACR_LOGIN_SERVER}/${service}:latest ../../phase-5/services/${service}/
    docker push ${ACR_LOGIN_SERVER}/${service}:latest
    print_success "${service} built and pushed"
done

# Update values file with ACR registry
print_status "Updating values file with ACR registry..."
cat > /tmp/aks-values.yaml <<EOF
global:
  imageRegistry: "${ACR_LOGIN_SERVER}/"
  environment: production

ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod

autoscaling:
  enabled: true

monitoring:
  enabled: true
EOF

# Deploy application
print_status "Deploying Todo App via Helm..."
helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
    --namespace ${NAMESPACE} \
    --values ${VALUES_FILE} \
    --values /tmp/aks-values.yaml \
    --wait \
    --timeout 15m

print_success "Todo App deployed successfully"

# Get ingress IP
print_status "Waiting for ingress IP..."
for i in {1..60}; do
    INGRESS_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$INGRESS_IP" ]; then
        break
    fi
    sleep 5
done

print_success "Deployment completed!"
echo ""
print_status "Ingress IP: ${INGRESS_IP}"
print_status "Update your DNS to point to this IP"
echo ""
print_status "Useful commands:"
echo "  kubectl get pods -n ${NAMESPACE}"
echo "  kubectl logs -f deployment/${RELEASE_NAME}-chat-api -n ${NAMESPACE}"
echo "  kubectl get ingress -n ${NAMESPACE}"
