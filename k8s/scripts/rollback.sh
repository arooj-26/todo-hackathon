#!/bin/bash
# Rollback script for Todo App Helm deployment
# This script safely rolls back to a previous release

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
NAMESPACE="${NAMESPACE:-todo-app}"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
REVISION="${1:-}"

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi

print_status "Rollback script for Todo App"
echo ""

# Show current release status
print_status "Current release status:"
helm status ${RELEASE_NAME} -n ${NAMESPACE}
echo ""

# Show release history
print_status "Release history:"
helm history ${RELEASE_NAME} -n ${NAMESPACE}
echo ""

# If no revision specified, ask user
if [ -z "$REVISION" ]; then
    echo "Which revision would you like to rollback to?"
    read -p "Enter revision number (or 'cancel' to abort): " REVISION

    if [ "$REVISION" = "cancel" ]; then
        print_warning "Rollback cancelled"
        exit 0
    fi
fi

# Validate revision number
if ! [[ "$REVISION" =~ ^[0-9]+$ ]]; then
    print_error "Invalid revision number: $REVISION"
    exit 1
fi

# Confirm rollback
print_warning "You are about to rollback ${RELEASE_NAME} in namespace ${NAMESPACE} to revision ${REVISION}"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_warning "Rollback cancelled"
    exit 0
fi

# Perform rollback
print_status "Rolling back to revision ${REVISION}..."
helm rollback ${RELEASE_NAME} ${REVISION} -n ${NAMESPACE} --wait --timeout 10m

if [ $? -eq 0 ]; then
    print_success "Rollback completed successfully"
else
    print_error "Rollback failed"
    exit 1
fi

# Verify rollback
print_status "Verifying rollback..."
sleep 10

# Check pod status
print_status "Checking pod status..."
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME}

# Check if all pods are running
TOTAL_PODS=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME} --no-headers | wc -l)
RUNNING_PODS=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/instance=${RELEASE_NAME} --field-selector=status.phase=Running --no-headers | wc -l)

echo ""
print_status "Pod status: ${RUNNING_PODS}/${TOTAL_PODS} running"

if [ ${RUNNING_PODS} -eq ${TOTAL_PODS} ]; then
    print_success "All pods are running"
else
    print_warning "Not all pods are running yet. Check pod status:"
    echo "  kubectl get pods -n ${NAMESPACE}"
    echo "  kubectl describe pod <pod-name> -n ${NAMESPACE}"
fi

# Show updated release status
echo ""
print_status "Updated release status:"
helm status ${RELEASE_NAME} -n ${NAMESPACE}

echo ""
print_success "Rollback process completed"
print_status "To check application health:"
echo "  kubectl get pods -n ${NAMESPACE}"
echo "  kubectl logs -f deployment/${RELEASE_NAME}-chat-api -n ${NAMESPACE}"
echo ""
print_status "If issues persist, you can rollback further:"
echo "  ./rollback.sh <previous-revision>"
