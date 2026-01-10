#!/bin/bash
# Google Kubernetes Engine (GKE) deployment script for Todo App
# This script deploys the complete system to Google GKE

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
PROJECT_ID="${PROJECT_ID:-your-project-id}"
CLUSTER_NAME="${CLUSTER_NAME:-todo-app-gke}"
REGION="${REGION:-us-central1}"
ZONE="${ZONE:-us-central1-a}"
NODE_COUNT="${NODE_COUNT:-3}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-2}"
NAMESPACE="${NAMESPACE:-todo-app}"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
CHART_PATH="../helm-charts/todo-app"
VALUES_FILE="../helm-charts/todo-app/values-cloud.yaml"

# Check prerequisites
print_status "Checking prerequisites..."
for cmd in gcloud kubectl helm; do
    if ! command -v $cmd &> /dev/null; then
        print_error "$cmd is not installed"
        exit 1
    fi
done
print_success "All prerequisites installed"

# Set project
print_status "Setting GCP project..."
gcloud config set project ${PROJECT_ID}
print_success "Project set to ${PROJECT_ID}"

# Enable required APIs
print_status "Enabling required GCP APIs..."
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
print_success "APIs enabled"

# Create GKE cluster
print_status "Creating GKE cluster (this may take 10-15 minutes)..."
if ! gcloud container clusters describe ${CLUSTER_NAME} --zone=${ZONE} &> /dev/null; then
    gcloud container clusters create ${CLUSTER_NAME} \
        --zone=${ZONE} \
        --num-nodes=${NODE_COUNT} \
        --machine-type=${MACHINE_TYPE} \
        --enable-autoscaling \
        --min-nodes=3 \
        --max-nodes=10 \
        --enable-autorepair \
        --enable-autoupgrade \
        --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver
    print_success "GKE cluster created"
else
    print_success "GKE cluster already exists"
fi

# Get GKE credentials
print_status "Getting GKE credentials..."
gcloud container clusters get-credentials ${CLUSTER_NAME} --zone=${ZONE}
print_success "Credentials configured"

# Install NGINX Ingress Controller
print_status "Installing NGINX Ingress Controller..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
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

# Build and push Docker images to GCR
print_status "Building and pushing Docker images to GCR..."
gcloud auth configure-docker

for service in chat-api recurring-tasks notifications audit frontend; do
    print_status "Building ${service}..."
    docker build -t gcr.io/${PROJECT_ID}/${service}:latest ../../phase-5/services/${service}/
    docker push gcr.io/${PROJECT_ID}/${service}:latest
    print_success "${service} built and pushed"
done

# Update values file with GCR registry
print_status "Updating values file with GCR registry..."
cat > /tmp/gke-values.yaml <<EOF
global:
  imageRegistry: "gcr.io/${PROJECT_ID}/"
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
    --values /tmp/gke-values.yaml \
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
