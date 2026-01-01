#!/bin/bash

# Todo App Kubernetes Deployment Script
# This script automates the complete deployment of the Todo App to Minikube

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() {
    print_message "$GREEN" "✅ $1"
}

print_error() {
    print_message "$RED" "❌ $1"
}

print_info() {
    print_message "$BLUE" "ℹ️  $1"
}

print_warning() {
    print_message "$YELLOW" "⚠️  $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    local missing_deps=()

    if ! command_exists docker; then
        missing_deps+=("docker")
    fi

    if ! command_exists minikube; then
        missing_deps+=("minikube")
    fi

    if ! command_exists kubectl; then
        missing_deps+=("kubectl")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_info "Please install the missing dependencies and try again."
        exit 1
    fi

    print_success "All prerequisites installed"
}

# Start Minikube cluster
start_minikube() {
    print_info "Checking Minikube status..."

    if minikube status >/dev/null 2>&1; then
        print_success "Minikube is already running"
    else
        print_info "Starting Minikube cluster..."
        minikube start --cpus=4 --memory=8192 --driver=docker
        print_success "Minikube cluster started"
    fi

    print_info "Enabling metrics-server addon..."
    minikube addons enable metrics-server
    print_success "Metrics-server enabled"
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."

    # Configure Docker to use Minikube's daemon
    print_info "Configuring Docker environment for Minikube..."
    eval $(minikube docker-env)

    # Build todo-backend
    print_info "Building todo-backend:v1..."
    docker build -t todo-backend:v1 ../todo-application/backend/
    print_success "todo-backend:v1 built"

    # Build todo-frontend
    print_info "Building todo-frontend:v1..."
    docker build -t todo-frontend:v1 ../todo-application/frontend/
    print_success "todo-frontend:v1 built"

    # Build chatbot-backend
    print_info "Building chatbot-backend:v1..."
    docker build -t chatbot-backend:v1 ../chatbot/backend/
    print_success "chatbot-backend:v1 built"

    # Build chatbot-frontend
    print_info "Building chatbot-frontend:v1..."
    docker build -t chatbot-frontend:v1 ../chatbot/frontend/
    print_success "chatbot-frontend:v1 built"

    print_success "All Docker images built successfully"
}

# Verify images
verify_images() {
    print_info "Verifying images in Minikube..."

    local images=("todo-backend:v1" "todo-frontend:v1" "chatbot-backend:v1" "chatbot-frontend:v1")
    local missing_images=()

    for image in "${images[@]}"; do
        if ! minikube ssh "docker images | grep -q ${image%:*}"; then
            missing_images+=("$image")
        fi
    done

    if [ ${#missing_images[@]} -ne 0 ]; then
        print_error "Missing images in Minikube: ${missing_images[*]}"
        return 1
    fi

    print_success "All images verified in Minikube"

    # Show image sizes
    print_info "Image sizes:"
    minikube ssh "docker images | grep -E 'REPOSITORY|todo|chatbot'"
}

# Deploy application
deploy_app() {
    print_info "Deploying application to Kubernetes..."

    # Apply rendered manifests
    kubectl apply -f rendered/

    print_success "Application deployed"
}

# Wait for pods to be ready
wait_for_pods() {
    print_info "Waiting for pods to be ready..."

    local timeout=300  # 5 minutes
    local elapsed=0
    local interval=5

    while [ $elapsed -lt $timeout ]; do
        local not_ready=$(kubectl get pods --no-headers 2>/dev/null | grep -v "Running" | wc -l)

        if [ "$not_ready" -eq 0 ]; then
            print_success "All pods are running"
            return 0
        fi

        echo -n "."
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo ""
    print_error "Timeout waiting for pods to be ready"
    kubectl get pods
    return 1
}

# Verify deployment
verify_deployment() {
    print_info "Verifying deployment..."

    echo ""
    print_info "Pods:"
    kubectl get pods

    echo ""
    print_info "Services:"
    kubectl get services

    echo ""
    print_info "Deployments:"
    kubectl get deployments

    echo ""
    print_info "Endpoints:"
    kubectl get endpoints

    # Check if all deployments are ready
    local not_ready=$(kubectl get deployments --no-headers 2>/dev/null | awk '{if ($2 != $4) print $1}')

    if [ -n "$not_ready" ]; then
        print_warning "Some deployments are not fully ready: $not_ready"
        return 1
    fi

    print_success "All deployments are ready"
}

# Show access information
show_access_info() {
    local minikube_ip=$(minikube ip)

    echo ""
    print_success "======================================"
    print_success "  Deployment Complete!"
    print_success "======================================"
    echo ""
    print_info "Minikube IP: $minikube_ip"
    echo ""
    print_info "Access your applications:"
    echo ""
    echo "  📝 Todo App Frontend:"
    echo "     http://$minikube_ip:30000"
    echo ""
    echo "  💬 Chatbot Frontend:"
    echo "     http://$minikube_ip:30001"
    echo ""
    print_info "Or use minikube service commands:"
    echo ""
    echo "  minikube service todo-frontend"
    echo "  minikube service chatbot-frontend"
    echo ""
    print_info "Useful commands:"
    echo ""
    echo "  kubectl get pods              # View pod status"
    echo "  kubectl logs <pod-name>       # View pod logs"
    echo "  kubectl describe pod <name>   # Debug pod issues"
    echo "  minikube dashboard            # Open Kubernetes dashboard"
    echo ""
    print_success "======================================"
}

# Show health status
show_health_status() {
    print_info "Checking application health..."

    echo ""
    print_info "PostgreSQL Status:"
    kubectl logs -l app=postgresql --tail=3 | grep -E "ready to accept connections|listening" || echo "Check logs manually"

    echo ""
    print_info "Todo Backend Health Checks:"
    kubectl logs -l app=todo-backend --tail=5 | grep -E "health|ready" || echo "Running..."

    echo ""
    print_info "Chatbot Backend Health Checks:"
    kubectl logs -l app=chatbot-backend --tail=5 | grep -E "health|ready" || echo "Running..."
}

# Main deployment flow
main() {
    echo ""
    print_info "======================================"
    print_info "  Todo App Kubernetes Deployment"
    print_info "======================================"
    echo ""

    check_prerequisites
    start_minikube
    build_images
    verify_images
    deploy_app
    wait_for_pods
    verify_deployment
    show_health_status
    show_access_info

    echo ""
    print_success "Deployment script completed successfully!"
    echo ""
}

# Run main function
main "$@"
