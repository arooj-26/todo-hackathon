#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Todo App - Oracle OKE Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration variables - set these before running
COMPARTMENT_ID="${COMPARTMENT_ID}"
CLUSTER_NAME="${CLUSTER_NAME:-todo-app-oke}"
REGION="${REGION:-us-ashburn-1}"
NODE_POOL_NAME="${NODE_POOL_NAME:-todo-app-nodepool}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_SHAPE="${NODE_SHAPE:-VM.Standard.E3.Flex}"
OCIR_REGION="${OCIR_REGION:-iad}"  # iad for Ashburn
NAMESPACE="todo-app"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Compartment ID: $COMPARTMENT_ID"
echo "  OKE Cluster: $CLUSTER_NAME"
echo "  Region: $REGION"
echo "  Node Count: $NODE_COUNT"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v oci >/dev/null 2>&1 || { echo -e "${RED}Error: OCI CLI not installed${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm not installed${NC}"; exit 1; }

if [ -z "$COMPARTMENT_ID" ]; then
    echo -e "${RED}Error: COMPARTMENT_ID environment variable must be set${NC}"
    echo "Example: export COMPARTMENT_ID=ocid1.compartment.oc1..xxx"
    exit 1
fi

# Create VCN (Virtual Cloud Network) for OKE
echo -e "${YELLOW}Creating VCN for OKE...${NC}"
VCN_ID=$(oci network vcn create \
  --compartment-id $COMPARTMENT_ID \
  --display-name "todo-app-vcn" \
  --cidr-block "10.0.0.0/16" \
  --query 'data.id' \
  --raw-output 2>/dev/null || echo "")

if [ -z "$VCN_ID" ]; then
    echo -e "${YELLOW}VCN might already exist, attempting to find it...${NC}"
    VCN_ID=$(oci network vcn list \
      --compartment-id $COMPARTMENT_ID \
      --display-name "todo-app-vcn" \
      --query 'data[0].id' \
      --raw-output)
fi

echo "VCN ID: $VCN_ID"

# Create OKE cluster (Quick Create recommended for simplicity)
echo -e "${YELLOW}Creating OKE cluster (this may take 10-15 minutes)...${NC}"
echo -e "${YELLOW}Note: Using OCI Console Quick Create is recommended for initial setup${NC}"
echo -e "${YELLOW}Visit: https://cloud.oracle.com/containers/clusters${NC}"

# Alternative: Use OCI CLI to create cluster
# oci ce cluster create \
#   --compartment-id $COMPARTMENT_ID \
#   --name $CLUSTER_NAME \
#   --vcn-id $VCN_ID \
#   --kubernetes-version v1.28.2 \
#   --wait-for-state ACTIVE

# Get cluster OCID (assuming cluster was created via console)
CLUSTER_OCID=$(oci ce cluster list \
  --compartment-id $COMPARTMENT_ID \
  --name $CLUSTER_NAME \
  --query 'data[0].id' \
  --raw-output 2>/dev/null || echo "")

if [ -z "$CLUSTER_OCID" ]; then
    echo -e "${RED}Error: Could not find OKE cluster. Please create it via OCI Console first.${NC}"
    echo -e "${YELLOW}After creating the cluster, run this script again.${NC}"
    exit 1
fi

echo "Cluster OCID: $CLUSTER_OCID"

# Get kubeconfig for OKE cluster
echo -e "${YELLOW}Getting kubeconfig for OKE cluster...${NC}"
mkdir -p ~/.kube
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file ~/.kube/config \
  --region $REGION \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Verify cluster connection
echo -e "${YELLOW}Verifying cluster connection...${NC}"
kubectl get nodes

# Login to OCIR (Oracle Cloud Infrastructure Registry)
echo -e "${YELLOW}Logging in to OCIR...${NC}"
TENANCY_NAMESPACE=$(oci os ns get --query 'data' --raw-output)
OCI_USERNAME=$(oci iam user list --query 'data[0]."name"' --raw-output)
OCI_AUTH_TOKEN="${OCI_AUTH_TOKEN}"

if [ -z "$OCI_AUTH_TOKEN" ]; then
    echo -e "${RED}Error: OCI_AUTH_TOKEN environment variable must be set${NC}"
    echo "Generate one at: https://cloud.oracle.com/identity/domains/my-profile/auth-tokens"
    exit 1
fi

docker login ${OCIR_REGION}.ocir.io -u ${TENANCY_NAMESPACE}/${OCI_USERNAME} -p ${OCI_AUTH_TOKEN}

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

# Build and push images to OCIR
echo -e "${YELLOW}Building and pushing Docker images to OCIR...${NC}"

cd ../../

# Build and push all images
for service in chat-api recurring-tasks notifications audit frontend; do
  echo -e "${YELLOW}Building $service...${NC}"
  docker build -t ${OCIR_REGION}.ocir.io/${TENANCY_NAMESPACE}/todo-app/$service:latest \
    -f services/$service/Dockerfile services/$service/
  docker push ${OCIR_REGION}.ocir.io/${TENANCY_NAMESPACE}/todo-app/$service:latest
done

cd k8s/scripts/

# Create namespace
echo -e "${YELLOW}Creating application namespace...${NC}"
kubectl create namespace $NAMESPACE || true

# Create image pull secret for OCIR
echo -e "${YELLOW}Creating OCIR image pull secret...${NC}"
kubectl create secret docker-registry ocir-secret \
  --docker-server=${OCIR_REGION}.ocir.io \
  --docker-username=${TENANCY_NAMESPACE}/${OCI_USERNAME} \
  --docker-password=${OCI_AUTH_TOKEN} \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy application with Helm
echo -e "${YELLOW}Deploying Todo App...${NC}"
helm upgrade --install todo-app ../helm-charts/todo-app/ \
  --namespace $NAMESPACE \
  --values ../helm-charts/todo-app/values-cloud.yaml \
  --set global.imageRegistry="${OCIR_REGION}.ocir.io/${TENANCY_NAMESPACE}" \
  --set global.imagePullSecrets[0].name=ocir-secret \
  --set cloudProvider.name="oracle" \
  --set cloudProvider.oracle.compartmentId="$COMPARTMENT_ID" \
  --set cloudProvider.oracle.okeClusterId="$CLUSTER_OCID" \
  --wait \
  --timeout 10m

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OKE Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Get Ingress IP
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo ""
echo -e "${GREEN}Access information:${NC}"
echo -e "  Ingress IP: $INGRESS_IP"
echo -e "  Configure DNS to point your domain to this IP"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Create Autonomous Database for PostgreSQL"
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
echo "  OCI console:     https://cloud.oracle.com/containers/clusters"
echo ""
