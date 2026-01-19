
 #!/bin/bash
# Minikube deployment script for Todo App with microservices architecture
# This script deploys the complete system to a local Minikube cluster

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"
RELEASE_NAME="todo-app"
CHART_PATH="../helm-charts/todo-app"
VALUES_FILE="../helm-charts/todo-app/values-minikube.yaml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists minikube; then
    print_error "Minikube is not installed. Please install Minikube first."
    exit 1
fi

if ! command_exists kubectl; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

if ! command_exists helm; then
    print_error "Helm is not installed. Please install Helm first."
    exit 1
fi

print_success "All prerequisites are installed"

# Check if Minikube is running
print_status "Checking Minikube status..."
if ! minikube status >/dev/null 2>&1; then
    print_warning "Minikube is not running. Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --driver=docker
    print_success "Minikube started"
else
    print_success "Minikube is already running"
fi

# Enable Minikube addons
print_status "Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server
print_success "Minikube addons enabled"

# Install Dapr
print_status "Checking Dapr installation..."
if ! kubectl get namespace dapr-system >/dev/null 2>&1; then
    print_status "Installing Dapr..."
    if command_exists dapr; then
        dapr init --kubernetes --wait
        print_success "Dapr installed successfully"
    else
        print_warning "Dapr CLI not found. Installing via Helm..."
        helm repo add dapr https://dapr.github.io/helm-charts/
        helm repo update
        helm install dapr dapr/dapr --version=1.12 --namespace dapr-system --create-namespace --wait
        print_success "Dapr installed via Helm"
    fi
else
    print_success "Dapr is already installed"
fi

# Install Strimzi Kafka Operator
print_status "Checking Strimzi Kafka installation..."
if ! kubectl get namespace kafka >/dev/null 2>&1; then
    print_status "Installing Strimzi Kafka Operator..."
    kubectl create namespace kafka
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

    # Wait for operator to be ready
    print_status "Waiting for Strimzi operator to be ready..."
    kubectl wait deployment/strimzi-cluster-operator --for=condition=Available --timeout=300s -n kafka

    print_success "Strimzi Kafka Operator installed"
else
    print_success "Strimzi Kafka is already installed"
fi

# Deploy Kafka cluster with KRaft (KafkaNodePool required for Strimzi 0.46+)
print_status "Checking Kafka cluster..."
if ! kubectl get kafka kafka-cluster -n kafka >/dev/null 2>&1; then
    print_status "Deploying Kafka cluster with KRaft mode..."

    # First, create KafkaNodePool (required by Strimzi 0.46+)
    cat <<EOF | kubectl apply -f - -n kafka
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: controller
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  replicas: 1
  roles:
    - controller
    - broker
  storage:
    type: ephemeral
EOF

    # Then create Kafka resource (without replicas, storage, zookeeper)
    cat <<EOF | kubectl apply -f - -n kafka
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  annotations:
    strimzi.io/kraft: enabled
    strimzi.io/node-pools: enabled
spec:
  kafka:
    version: 4.1.0
    metadataVersion: 4.1-IV0
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

    print_status "Waiting for Kafka cluster to be ready..."
    kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka

    print_success "Kafka cluster deployed with KRaft"
else
    print_success "Kafka cluster is already deployed"
fi

# Create Kafka topics
print_status "Creating Kafka topics..."
cat <<EOF | kubectl apply -f - -n kafka
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
EOF
print_success "Kafka topics created"

# Build Docker images in Minikube's Docker daemon
print_status "Building Docker images..."
eval $(minikube docker-env)

# Build all service images
print_status "Building chat-api image..."
docker build -t chat-api:latest ../../phase-5/services/chat-api/ || print_warning "Failed to build chat-api image"

print_status "Building recurring-tasks image..."
docker build -t recurring-tasks:latest ../../phase-5/services/recurring-tasks/ || print_warning "Failed to build recurring-tasks image"

print_status "Building notifications image..."
docker build -t notifications:latest ../../phase-5/services/notifications/ || print_warning "Failed to build notifications image"

print_status "Building audit image..."
docker build -t audit:latest ../../phase-5/services/audit/ || print_warning "Failed to build audit image"

print_status "Building frontend image..."
docker build -t frontend:latest ../../phase-5/services/frontend/ || print_warning "Failed to build frontend image"

print_success "Docker images built"

# Install/Upgrade Helm chart
print_status "Deploying Todo App via Helm..."
helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
    --namespace ${NAMESPACE} \
    --values ${VALUES_FILE} \
    --wait \
    --timeout 10m

print_success "Todo App deployed successfully"

# Display deployment information
print_status "Deployment Information:"
echo ""
echo "Namespace: ${NAMESPACE}"
echo "Release Name: ${RELEASE_NAME}"
echo ""
echo "Services:"
kubectl get services -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
echo ""
echo "Pods:"
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}
echo ""

# Get Minikube IP and NodePort
MINIKUBE_IP=$(minikube ip)
FRONTEND_PORT=$(kubectl get service ${RELEASE_NAME}-frontend -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}')

print_success "Deployment completed successfully!"
echo ""
print_status "Access the application at: http://${MINIKUBE_IP}:${FRONTEND_PORT}"
echo ""
print_status "To view logs, use:"
echo "  kubectl logs -f deployment/${RELEASE_NAME}-chat-api -n ${NAMESPACE}"
echo ""
print_status "To run validation script:"
echo "  ./validate-deployment.sh"
