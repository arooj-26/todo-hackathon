#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Todo App - Minikube Deployment${NC}"
echo -e "${GREEN}=================================${NC}"

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo -e "${RED}Error: minikube is not installed${NC}"
    echo "Please install minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: helm is not installed${NC}"
    echo "Please install helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Start minikube if not running
echo -e "${YELLOW}Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --cpus=4 --memory=8192 --driver=docker
else
    echo -e "${GREEN}Minikube is already running${NC}"
fi

# Enable necessary addons
echo -e "${YELLOW}Enabling Minikube addons...${NC}"
minikube addons enable metrics-server
minikube addons enable ingress

# Set kubectl context to minikube
echo -e "${YELLOW}Setting kubectl context to minikube...${NC}"
kubectl config use-context minikube

# Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Install Dapr
echo -e "${YELLOW}Installing Dapr...${NC}"
if ! helm list -n dapr-system | grep -q dapr; then
    helm repo add dapr https://dapr.github.io/helm-charts/ || true
    helm repo update
    helm upgrade --install dapr dapr/dapr \
        --namespace dapr-system \
        --create-namespace \
        --wait \
        --timeout 10m
    echo -e "${GREEN}Dapr installed successfully${NC}"
else
    echo -e "${GREEN}Dapr is already installed${NC}"
fi

# Install Strimzi Kafka Operator
echo -e "${YELLOW}Installing Strimzi Kafka Operator...${NC}"
if ! kubectl get namespace kafka &> /dev/null; then
    kubectl create namespace kafka
    kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
    echo -e "${YELLOW}Waiting for Strimzi operator to be ready...${NC}"
    kubectl wait --for=condition=available --timeout=300s deployment/strimzi-cluster-operator -n kafka
    echo -e "${GREEN}Strimzi operator installed successfully${NC}"
else
    echo -e "${GREEN}Strimzi operator is already installed${NC}"
fi

# Deploy Kafka cluster
echo -e "${YELLOW}Deploying Kafka cluster...${NC}"
kubectl apply -f ../kafka/kafka-cluster.yaml -n kafka
echo -e "${YELLOW}Waiting for Kafka cluster to be ready (this may take a few minutes)...${NC}"
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka || true

# Create Kafka topics
echo -e "${YELLOW}Creating Kafka topics...${NC}"
kubectl apply -f ../kafka/kafka-topics.yaml -n kafka
echo -e "${YELLOW}Waiting for Kafka topics to be ready...${NC}"
sleep 10  # Give topics time to be created

# Deploy PostgreSQL
echo -e "${YELLOW}Deploying PostgreSQL...${NC}"
cat <<EOF | kubectl apply -f -
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
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        emptyDir: {}
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
  type: ClusterIP
EOF

echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n todo-app

# Build Docker images in Minikube
echo -e "${YELLOW}Building Docker images in Minikube...${NC}"
eval $(minikube docker-env)

# Navigate to project root
cd ../../

# Build backend services
echo -e "${YELLOW}Building Chat API image...${NC}"
docker build -t todo-app/chat-api:latest -f services/chat-api/Dockerfile services/chat-api/

echo -e "${YELLOW}Building Recurring Tasks image...${NC}"
docker build -t todo-app/recurring-tasks:latest -f services/recurring-tasks/Dockerfile services/recurring-tasks/

echo -e "${YELLOW}Building Notifications image...${NC}"
docker build -t todo-app/notifications:latest -f services/notifications/Dockerfile services/notifications/

echo -e "${YELLOW}Building Audit image...${NC}"
docker build -t todo-app/audit:latest -f services/audit/Dockerfile services/audit/

echo -e "${YELLOW}Building Frontend image...${NC}"
docker build -t todo-app/frontend:latest -f services/frontend/Dockerfile services/frontend/

# Go back to scripts directory
cd k8s/scripts/

# Deploy Todo App using Helm
echo -e "${YELLOW}Deploying Todo App with Helm...${NC}"
helm upgrade --install todo-app ../helm-charts/todo-app/ \
    --namespace todo-app \
    --values ../helm-charts/todo-app/values-minikube.yaml \
    --wait \
    --timeout 10m

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=================================${NC}"

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

echo ""
echo -e "${GREEN}Access the application:${NC}"
echo -e "  Frontend:  http://$MINIKUBE_IP:30000"
echo -e "  Chat API:  http://$MINIKUBE_IP:30080"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View pods:           kubectl get pods -n todo-app"
echo "  View services:       kubectl get svc -n todo-app"
echo "  View logs:           kubectl logs -n todo-app <pod-name>"
echo "  Dapr dashboard:      dapr dashboard -k -n todo-app"
echo ""
echo -e "${GREEN}Run validation:${NC}"
echo "  ./validate-deployment.sh"
echo ""
