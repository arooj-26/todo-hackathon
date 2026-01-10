#!/bin/bash
# Deploy monitoring stack for Todo App
# This script deploys Prometheus, Grafana, and Zipkin for observability

set -e

# Colors
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
NAMESPACE="${NAMESPACE:-monitoring}"

print_status "Deploying monitoring stack..."

# Create namespace
print_status "Creating monitoring namespace..."
kubectl create namespace ${NAMESPACE} || print_warning "Namespace might already exist"

# Add Helm repos
print_status "Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus stack
print_status "Installing Prometheus and Grafana..."
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --namespace ${NAMESPACE} \
    --values ./prometheus/prometheus-values.yaml \
    --wait \
    --timeout 10m

print_success "Prometheus and Grafana installed"

# Apply service monitors
print_status "Applying service monitors..."
kubectl apply -f ./prometheus/service-monitors.yaml

# Apply alert rules
print_status "Applying alert rules..."
kubectl apply -f ./prometheus/alert-rules.yaml

print_success "Monitoring configuration applied"

# Deploy Zipkin for distributed tracing
print_status "Deploying Zipkin..."
kubectl apply -f ./zipkin/zipkin-deployment.yaml

print_success "Zipkin deployed"

# Display access information
print_status "Getting service URLs..."

# Port forward commands
echo ""
print_success "Monitoring stack deployed successfully!"
echo ""
print_status "Access Grafana:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/prometheus-grafana 3000:80"
echo "  Username: admin"
echo "  Password: admin (change this in production!)"
echo ""
print_status "Access Prometheus:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo ""
print_status "Access Zipkin:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/zipkin 9411:9411"
echo ""
print_status "View alerts:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/prometheus-kube-prometheus-alertmanager 9093:9093"
