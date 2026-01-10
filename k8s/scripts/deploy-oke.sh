#!/bin/bash
# Oracle Kubernetes Engine (OKE) deployment script for Todo App
# This script deploys the complete system to Oracle OKE

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
COMPARTMENT_ID="${COMPARTMENT_ID:-your-compartment-id}"
CLUSTER_NAME="${CLUSTER_NAME:-todo-app-oke}"
REGION="${REGION:-us-ashburn-1}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_SHAPE="${NODE_SHAPE:-VM.Standard.E4.Flex}"
OCIR_REGION="${OCIR_REGION:-iad}"  # iad for Ashburn
NAMESPACE="${NAMESPACE:-todo-app}"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
CHART_PATH="../helm-charts/todo-app"
VALUES_FILE="../helm-charts/todo-app/values-cloud.yaml"

# Check prerequisites
print_status "Checking prerequisites..."
for cmd in oci kubectl helm; do
    if ! command -v $cmd &> /dev/null; then
        print_error "$cmd is not installed"
        exit 1
    fi
done
print_success "All prerequisites installed"

# Note: OKE cluster creation via CLI is complex
# Recommend creating cluster via OCI Console first
print_warning "This script assumes OKE cluster is already created"
print_status "Please ensure your OKE cluster '${CLUSTER_NAME}' exists in ${REGION}"

# Get OKE cluster credentials
print_status "Getting OKE cluster credentials..."
CLUSTER_ID=$(oci ce cluster list --compartment-id ${COMPARTMENT_ID} --name ${CLUSTER_NAME} --query 'data[0].id' --raw-output)
if [ -z "$CLUSTER_ID" ]; then
    print_error "Cluster not found. Please create cluster first."
    exit 1
fi

oci ce cluster create-kubeconfig \
    --cluster-id ${CLUSTER_ID} \
    --file $HOME/.kube/config \
    --region ${REGION} \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT
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

# Login to OCIR
print_status "Logging in to Oracle Container Registry..."
TENANCY_NAMESPACE=$(oci os ns get --query 'data' --raw-output)
OCIR_USERNAME="${TENANCY_NAMESPACE}/oracleidentitycloudservice/$(oci iam user list --query 'data[0].name' --raw-output)"
echo "Please enter your Auth Token:"
read -s OCIR_PASSWORD
docker login ${OCIR_REGION}.ocir.io -u ${OCIR_USERNAME} -p ${OCIR_PASSWORD}
print_success "Logged in to OCIR"

# Build and push Docker images to OCIR
print_status "Building and pushing Docker images to OCIR..."
for service in chat-api recurring-tasks notifications audit frontend; do
    print_status "Building ${service}..."
    docker build -t ${OCIR_REGION}.ocir.io/${TENANCY_NAMESPACE}/todo-app/${service}:latest ../../phase-5/services/${service}/
    docker push ${OCIR_REGION}.ocir.io/${TENANCY_NAMESPACE}/todo-app/${service}:latest
    print_success "${service} built and pushed"
done

# Create image pull secret
kubectl create secret docker-registry ocir-secret \
    --docker-server=${OCIR_REGION}.ocir.io \
    --docker-username=${OCIR_USERNAME} \
    --docker-password=${OCIR_PASSWORD} \
    --namespace=${NAMESPACE} \
    --dry-run=client -o yaml | kubectl apply -f -

# Update values file with OCIR registry
print_status "Updating values file with OCIR registry..."
cat > /tmp/oke-values.yaml <<EOF
global:
  imageRegistry: "${OCIR_REGION}.ocir.io/${TENANCY_NAMESPACE}/todo-app/"
  environment: production
  imagePullSecrets:
    - name: ocir-secret

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
    --values /tmp/oke-values.yaml \
    --wait \
    --timeout 15m

print_success "Todo App deployed successfully"

# Get load balancer IP
print_status "Waiting for load balancer IP..."
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
