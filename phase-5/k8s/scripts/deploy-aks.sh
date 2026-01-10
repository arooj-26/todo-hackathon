#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Todo App - Azure AKS Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration variables - set these before running
RESOURCE_GROUP="${RESOURCE_GROUP:-todo-app-rg}"
AKS_CLUSTER_NAME="${AKS_CLUSTER_NAME:-todo-app-aks}"
ACR_NAME="${ACR_NAME:-todoappackr}"
LOCATION="${LOCATION:-eastus}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_VM_SIZE="${NODE_VM_SIZE:-Standard_D2s_v3}"
NAMESPACE="todo-app"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  AKS Cluster: $AKS_CLUSTER_NAME"
echo "  ACR Name: $ACR_NAME"
echo "  Location: $LOCATION"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v az >/dev/null 2>&1 || { echo -e "${RED}Error: Azure CLI not installed${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm not installed${NC}"; exit 1; }

# Login to Azure
echo -e "${YELLOW}Logging in to Azure...${NC}"
az login || { echo -e "${RED}Azure login failed${NC}"; exit 1; }

# Create resource group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create Azure Container Registry (ACR)
echo -e "${YELLOW}Creating Azure Container Registry...${NC}"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard \
  --location $LOCATION

# Create AKS cluster with managed identity
echo -e "${YELLOW}Creating AKS cluster (this may take 10-15 minutes)...${NC}"
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME \
  --node-count $NODE_COUNT \
  --node-vm-size $NODE_VM_SIZE \
  --enable-managed-identity \
  --attach-acr $ACR_NAME \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --location $LOCATION

# Get AKS credentials
echo -e "${YELLOW}Getting AKS credentials...${NC}"
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME \
  --overwrite-existing

# Verify cluster connection
echo -e "${YELLOW}Verifying cluster connection...${NC}"
kubectl get nodes

# Install NGINX Ingress Controller
echo -e "${YELLOW}Installing NGINX Ingress Controller...${NC}"
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
  --wait

# Install cert-manager for TLS certificates
echo -e "${YELLOW}Installing cert-manager...${NC}"
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true \
  --wait

# Install Dapr
echo -e "${YELLOW}Installing Dapr...${NC}"
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait \
  --timeout 10m

# Install Strimzi Kafka Operator
echo -e "${YELLOW}Installing Strimzi Kafka Operator...${NC}"
kubectl create namespace kafka || true
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

echo -e "${YELLOW}Waiting for Strimzi operator...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/strimzi-cluster-operator -n kafka

# Deploy Kafka cluster
echo -e "${YELLOW}Deploying Kafka cluster...${NC}"
kubectl apply -f ../kafka/kafka-cluster.yaml -n kafka

echo -e "${YELLOW}Waiting for Kafka cluster (this may take 5-10 minutes)...${NC}"
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka || true

# Create Kafka topics
echo -e "${YELLOW}Creating Kafka topics...${NC}"
kubectl apply -f ../kafka/kafka-topics.yaml -n kafka

# Build and push images to ACR
echo -e "${YELLOW}Building and pushing Docker images to ACR...${NC}"
az acr login --name $ACR_NAME

cd ../../

# Build and push all images
for service in chat-api recurring-tasks notifications audit frontend; do
  echo -e "${YELLOW}Building $service...${NC}"
  docker build -t $ACR_NAME.azurecr.io/todo-app/$service:latest \
    -f services/$service/Dockerfile services/$service/
  docker push $ACR_NAME.azurecr.io/todo-app/$service:latest
done

cd k8s/scripts/

# Create namespace
echo -e "${YELLOW}Creating application namespace...${NC}"
kubectl create namespace $NAMESPACE || true

# Create Azure Database for PostgreSQL (optional - or use existing)
echo -e "${YELLOW}Note: Make sure to create Azure Database for PostgreSQL separately${NC}"
echo -e "${YELLOW}Set the DATABASE_URL secret before deploying the application${NC}"

# Deploy application with Helm
echo -e "${YELLOW}Deploying Todo App...${NC}"
helm upgrade --install todo-app ../helm-charts/todo-app/ \
  --namespace $NAMESPACE \
  --values ../helm-charts/todo-app/values-cloud.yaml \
  --set global.imageRegistry="$ACR_NAME.azurecr.io" \
  --set cloudProvider.name="azure" \
  --set cloudProvider.azure.resourceGroup="$RESOURCE_GROUP" \
  --set cloudProvider.azure.aksClusterName="$AKS_CLUSTER_NAME" \
  --set cloudProvider.azure.acrName="$ACR_NAME" \
  --wait \
  --timeout 10m

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AKS Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Get Ingress IP
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo ""
echo -e "${GREEN}Access information:${NC}"
echo -e "  Ingress IP: $INGRESS_IP"
echo -e "  Configure DNS to point your domain to this IP"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Configure DNS: Add A record for your domain pointing to $INGRESS_IP"
echo "  2. Update values-cloud.yaml with your domain name"
echo "  3. Create database secret: kubectl create secret -n $NAMESPACE ..."
echo "  4. Redeploy with domain: helm upgrade ..."
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View pods:       kubectl get pods -n $NAMESPACE"
echo "  View services:   kubectl get svc -n $NAMESPACE"
echo "  View ingress:    kubectl get ingress -n $NAMESPACE"
echo "  View logs:       kubectl logs -n $NAMESPACE <pod-name>"
echo ""
