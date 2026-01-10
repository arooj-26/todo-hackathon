#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Todo App - Google GKE Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration variables - set these before running
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}"
CLUSTER_NAME="${CLUSTER_NAME:-todo-app-gke}"
REGION="${REGION:-us-central1}"
ZONE="${ZONE:-us-central1-a}"
NODE_COUNT="${NODE_COUNT:-3}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-2}"
NAMESPACE="todo-app"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  GKE Cluster: $CLUSTER_NAME"
echo "  Region: $REGION"
echo "  Zone: $ZONE"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v gcloud >/dev/null 2>&1 || { echo -e "${RED}Error: gcloud CLI not installed${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm not installed${NC}"; exit 1; }

# Login to GCP
echo -e "${YELLOW}Logging in to Google Cloud...${NC}"
gcloud auth login || { echo -e "${RED}GCP login failed${NC}"; exit 1; }

# Set project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required GCP APIs...${NC}"
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable compute.googleapis.com

# Create GKE cluster
echo -e "${YELLOW}Creating GKE cluster (this may take 10-15 minutes)...${NC}"
gcloud container clusters create $CLUSTER_NAME \
  --zone $ZONE \
  --num-nodes $NODE_COUNT \
  --machine-type $MACHINE_TYPE \
  --enable-cloud-logging \
  --enable-cloud-monitoring \
  --enable-ip-alias \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --workload-pool=$PROJECT_ID.svc.id.goog

# Get GKE credentials
echo -e "${YELLOW}Getting GKE credentials...${NC}"
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE

# Verify cluster connection
echo -e "${YELLOW}Verifying cluster connection...${NC}"
kubectl get nodes

# Configure Docker for GCR
echo -e "${YELLOW}Configuring Docker for GCR...${NC}"
gcloud auth configure-docker

# Install NGINX Ingress Controller
echo -e "${YELLOW}Installing NGINX Ingress Controller...${NC}"
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
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

# Build and push images to GCR
echo -e "${YELLOW}Building and pushing Docker images to GCR...${NC}"

cd ../../

# Build and push all images
for service in chat-api recurring-tasks notifications audit frontend; do
  echo -e "${YELLOW}Building $service...${NC}"
  docker build -t gcr.io/$PROJECT_ID/todo-app/$service:latest \
    -f services/$service/Dockerfile services/$service/
  docker push gcr.io/$PROJECT_ID/todo-app/$service:latest
done

cd k8s/scripts/

# Create namespace
echo -e "${YELLOW}Creating application namespace...${NC}"
kubectl create namespace $NAMESPACE || true

# Create Workload Identity binding (for GCP service access)
echo -e "${YELLOW}Configuring Workload Identity...${NC}"
kubectl create serviceaccount todo-app-sa -n $NAMESPACE || true

gcloud iam service-accounts create todo-app-gsa \
  --display-name="Todo App Service Account" || true

gcloud iam service-accounts add-iam-policy-binding \
  todo-app-gsa@$PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[$NAMESPACE/todo-app-sa]" || true

kubectl annotate serviceaccount todo-app-sa -n $NAMESPACE \
  iam.gke.io/gcp-service-account=todo-app-gsa@$PROJECT_ID.iam.gserviceaccount.com \
  --overwrite || true

# Deploy application with Helm
echo -e "${YELLOW}Deploying Todo App...${NC}"
helm upgrade --install todo-app ../helm-charts/todo-app/ \
  --namespace $NAMESPACE \
  --values ../helm-charts/todo-app/values-cloud.yaml \
  --set global.imageRegistry="gcr.io/$PROJECT_ID" \
  --set cloudProvider.name="gcp" \
  --set cloudProvider.gcp.projectId="$PROJECT_ID" \
  --set cloudProvider.gcp.gkeClusterName="$CLUSTER_NAME" \
  --wait \
  --timeout 10m

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}GKE Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Get Ingress IP
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo ""
echo -e "${GREEN}Access information:${NC}"
echo -e "  Ingress IP: $INGRESS_IP"
echo -e "  Configure DNS to point your domain to this IP"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Create Cloud SQL PostgreSQL instance"
echo "  2. Configure DNS: Add A record for your domain pointing to $INGRESS_IP"
echo "  3. Update values-cloud.yaml with your domain name"
echo "  4. Create database secret: kubectl create secret -n $NAMESPACE ..."
echo "  5. Redeploy with domain: helm upgrade ..."
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View pods:       kubectl get pods -n $NAMESPACE"
echo "  View services:   kubectl get svc -n $NAMESPACE"
echo "  View ingress:    kubectl get ingress -n $NAMESPACE"
echo "  View logs:       kubectl logs -n $NAMESPACE <pod-name>"
echo "  GKE console:     https://console.cloud.google.com/kubernetes/clusters/details/$ZONE/$CLUSTER_NAME"
echo ""
