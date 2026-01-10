#!/bin/bash
# Validation script for Todo App deployment
# Checks if all pods are running and health checks are passing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-default}"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
TIMEOUT=300  # 5 minutes timeout

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Track validation results
VALIDATION_PASSED=true

print_status "Starting validation of Todo App deployment..."
echo ""

# 1. Check if namespace exists
print_status "Checking namespace: ${NAMESPACE}"
if kubectl get namespace ${NAMESPACE} >/dev/null 2>&1; then
    print_success "Namespace ${NAMESPACE} exists"
else
    print_error "Namespace ${NAMESPACE} does not exist"
    VALIDATION_PASSED=false
fi
echo ""

# 2. Check Helm release
print_status "Checking Helm release: ${RELEASE_NAME}"
if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    RELEASE_STATUS=$(helm list -n ${NAMESPACE} | grep ${RELEASE_NAME} | awk '{print $8}')
    if [ "${RELEASE_STATUS}" == "deployed" ]; then
        print_success "Helm release ${RELEASE_NAME} is deployed"
    else
        print_warning "Helm release ${RELEASE_NAME} status: ${RELEASE_STATUS}"
    fi
else
    print_error "Helm release ${RELEASE_NAME} not found"
    VALIDATION_PASSED=false
fi
echo ""

# 3. Check all pods are running
print_status "Checking pod status..."
SERVICES=("chat-api" "recurring-tasks" "notifications" "audit" "frontend" "postgresql")

for service in "${SERVICES[@]}"; do
    POD_NAME="${RELEASE_NAME}-${service}"
    POD_COUNT=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} --no-headers 2>/dev/null | wc -l)

    if [ ${POD_COUNT} -eq 0 ]; then
        print_error "No pods found for ${service}"
        VALIDATION_PASSED=false
        continue
    fi

    # Check if all pods are running
    RUNNING_COUNT=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)

    if [ ${RUNNING_COUNT} -eq ${POD_COUNT} ]; then
        print_success "${service}: ${RUNNING_COUNT}/${POD_COUNT} pods running"
    else
        print_error "${service}: ${RUNNING_COUNT}/${POD_COUNT} pods running"
        VALIDATION_PASSED=false

        # Show pod status
        kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service}
    fi
done
echo ""

# 4. Check services
print_status "Checking services..."
for service in "${SERVICES[@]}"; do
    if kubectl get service ${RELEASE_NAME}-${service} -n ${NAMESPACE} >/dev/null 2>&1; then
        print_success "Service ${service} exists"
    else
        print_error "Service ${service} not found"
        VALIDATION_PASSED=false
    fi
done
echo ""

# 5. Check Dapr sidecars
print_status "Checking Dapr sidecars..."
DAPR_SERVICES=("chat-api" "recurring-tasks" "notifications" "audit")

for service in "${DAPR_SERVICES[@]}"; do
    POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "${POD_NAME}" ]; then
        print_warning "No pod found for ${service} to check Dapr sidecar"
        continue
    fi

    CONTAINER_COUNT=$(kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.containers[*].name}' 2>/dev/null | wc -w)

    if [ ${CONTAINER_COUNT} -ge 2 ]; then
        print_success "${service}: Dapr sidecar is present (${CONTAINER_COUNT} containers)"
    else
        print_warning "${service}: Dapr sidecar might be missing (${CONTAINER_COUNT} containers)"
    fi
done
echo ""

# 6. Check Dapr components
print_status "Checking Dapr components..."
DAPR_COMPONENTS=("kafka-pubsub" "statestore" "kubernetes-secrets")

for component in "${DAPR_COMPONENTS[@]}"; do
    if kubectl get component ${component} -n ${NAMESPACE} >/dev/null 2>&1; then
        print_success "Dapr component ${component} exists"
    else
        print_warning "Dapr component ${component} not found"
    fi
done
echo ""

# 7. Check Kafka cluster
print_status "Checking Kafka cluster..."
if kubectl get kafka kafka-cluster -n kafka >/dev/null 2>&1; then
    KAFKA_STATUS=$(kubectl get kafka kafka-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
    if [ "${KAFKA_STATUS}" == "True" ]; then
        print_success "Kafka cluster is ready"
    else
        print_warning "Kafka cluster is not ready yet"
    fi
else
    print_error "Kafka cluster not found"
    VALIDATION_PASSED=false
fi
echo ""

# 8. Check Kafka topics
print_status "Checking Kafka topics..."
KAFKA_TOPICS=("task-events" "reminders" "task-updates")

for topic in "${KAFKA_TOPICS[@]}"; do
    if kubectl get kafkatopic ${topic} -n kafka >/dev/null 2>&1; then
        print_success "Kafka topic ${topic} exists"
    else
        print_error "Kafka topic ${topic} not found"
        VALIDATION_PASSED=false
    fi
done
echo ""

# 9. Check ConfigMaps and Secrets
print_status "Checking ConfigMaps and Secrets..."
if kubectl get configmap ${RELEASE_NAME}-config -n ${NAMESPACE} >/dev/null 2>&1; then
    print_success "ConfigMap exists"
else
    print_error "ConfigMap not found"
    VALIDATION_PASSED=false
fi

if kubectl get secret ${RELEASE_NAME}-secrets -n ${NAMESPACE} >/dev/null 2>&1; then
    print_success "Secrets exist"
else
    print_error "Secrets not found"
    VALIDATION_PASSED=false
fi
echo ""

# 10. Test health endpoints
print_status "Testing health endpoints..."
for service in "chat-api" "recurring-tasks" "notifications" "audit"; do
    POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "${POD_NAME}" ]; then
        print_warning "No pod found for ${service} to test health endpoint"
        continue
    fi

    # Get the port for the service
    case ${service} in
        chat-api) PORT=8000 ;;
        recurring-tasks) PORT=8001 ;;
        notifications) PORT=8002 ;;
        audit) PORT=8003 ;;
    esac

    HEALTH_STATUS=$(kubectl exec ${POD_NAME} -n ${NAMESPACE} -c ${service} -- curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}/health 2>/dev/null || echo "000")

    if [ "${HEALTH_STATUS}" == "200" ]; then
        print_success "${service}: Health check passed (HTTP ${HEALTH_STATUS})"
    else
        print_warning "${service}: Health check returned HTTP ${HEALTH_STATUS}"
    fi
done
echo ""

# 11. Check PVC for PostgreSQL
print_status "Checking PostgreSQL PVC..."
if kubectl get pvc ${RELEASE_NAME}-postgresql-pvc -n ${NAMESPACE} >/dev/null 2>&1; then
    PVC_STATUS=$(kubectl get pvc ${RELEASE_NAME}-postgresql-pvc -n ${NAMESPACE} -o jsonpath='{.status.phase}')
    if [ "${PVC_STATUS}" == "Bound" ]; then
        print_success "PostgreSQL PVC is bound"
    else
        print_warning "PostgreSQL PVC status: ${PVC_STATUS}"
    fi
else
    print_warning "PostgreSQL PVC not found (might be using emptyDir)"
fi
echo ""

# Final summary
echo "========================================"
if [ "${VALIDATION_PASSED}" == "true" ]; then
    print_success "All validation checks passed!"
    echo ""
    print_status "Application is ready to use"

    # Display access information
    if command -v minikube >/dev/null 2>&1; then
        MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "localhost")
        FRONTEND_PORT=$(kubectl get service ${RELEASE_NAME}-frontend -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "30000")
        echo ""
        print_status "Access the application at: http://${MINIKUBE_IP}:${FRONTEND_PORT}"
    fi

    exit 0
else
    print_error "Some validation checks failed!"
    echo ""
    print_status "Please review the errors above and check:"
    echo "  - Pod logs: kubectl logs -f <pod-name> -n ${NAMESPACE}"
    echo "  - Pod details: kubectl describe pod <pod-name> -n ${NAMESPACE}"
    echo "  - Events: kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp'"
    exit 1
fi
