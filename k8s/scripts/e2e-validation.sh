#!/bin/bash
# End-to-end validation following quickstart.md
# Comprehensive validation of entire system

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

NAMESPACE="${NAMESPACE:-todo-app}"
API_URL="${API_URL:-http://localhost:8000}"
FAILED=0

print_status "Starting end-to-end validation..."
echo ""

# Step 1: Check infrastructure
print_status "Step 1: Validating infrastructure..."

# Check Kubernetes cluster
if ! kubectl cluster-info &>/dev/null; then
    print_error "Kubernetes cluster not accessible"
    exit 1
fi
print_success "Kubernetes cluster accessible"

# Check Dapr
if kubectl get pods -n dapr-system &>/dev/null; then
    DAPR_PODS=$(kubectl get pods -n dapr-system --field-selector=status.phase=Running --no-headers | wc -l)
    if [ ${DAPR_PODS} -gt 0 ]; then
        print_success "Dapr control plane running (${DAPR_PODS} pods)"
    else
        print_error "Dapr control plane not running"
        FAILED=1
    fi
else
    print_error "Dapr not deployed"
    FAILED=1
fi

# Check Kafka
if kubectl get kafka kafka-cluster -n kafka &>/dev/null; then
    print_success "Kafka cluster deployed"
else
    print_warning "Kafka not deployed"
fi

# Step 2: Check application deployment
print_status "Step 2: Validating application deployment..."

SERVICES=("chat-api" "recurring-tasks" "notifications" "audit" "frontend")

for service in "${SERVICES[@]}"; do
    POD_COUNT=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)

    if [ ${POD_COUNT} -gt 0 ]; then
        print_success "${service}: ${POD_COUNT} pod(s) running"
    else
        print_error "${service}: No running pods"
        FAILED=1
    fi
done

# Step 3: Health checks
print_status "Step 3: Running health checks..."

for service in chat-api recurring-tasks notifications audit; do
    POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "${POD}" ]; then
        continue
    fi

    case ${service} in
        chat-api) PORT=8000 ;;
        recurring-tasks) PORT=8001 ;;
        notifications) PORT=8002 ;;
        audit) PORT=8003 ;;
    esac

    STATUS=$(kubectl exec ${POD} -n ${NAMESPACE} -c ${service} -- curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}/health 2>/dev/null || echo "000")

    if [ "${STATUS}" == "200" ]; then
        print_success "${service}: Health check passed"
    else
        print_error "${service}: Health check failed (HTTP ${STATUS})"
        FAILED=1
    fi
done

# Step 4: API functionality tests
print_status "Step 4: Testing API functionality..."

# Port forward chat-api for testing
print_status "Setting up port forward..."
kubectl port-forward -n ${NAMESPACE} svc/todo-app-chat-api 8000:8000 >/dev/null 2>&1 &
PF_PID=$!
sleep 3

# Cleanup function
cleanup() {
    if [ -n "${PF_PID}" ]; then
        kill ${PF_PID} 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Test 1: Create task
print_status "Test 1: Creating a task..."
CREATE_RESPONSE=$(curl -s -X POST ${API_URL}/api/tasks \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Task","description":"E2E validation task","priority":"high"}' \
    -w "\n%{http_code}" 2>/dev/null || echo "000")

HTTP_CODE=$(echo "${CREATE_RESPONSE}" | tail -1)
TASK_BODY=$(echo "${CREATE_RESPONSE}" | head -n -1)

if [ "${HTTP_CODE}" == "201" ]; then
    TASK_ID=$(echo "${TASK_BODY}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")
    if [ -n "${TASK_ID}" ]; then
        print_success "Task created (ID: ${TASK_ID})"
    else
        print_error "Task creation response missing ID"
        FAILED=1
    fi
else
    print_error "Failed to create task (HTTP ${HTTP_CODE})"
    FAILED=1
fi

# Test 2: List tasks
print_status "Test 2: Listing tasks..."
LIST_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/api/tasks 2>/dev/null || echo "000")

if [ "${LIST_RESPONSE}" == "200" ]; then
    print_success "Tasks listed successfully"
else
    print_error "Failed to list tasks (HTTP ${LIST_RESPONSE})"
    FAILED=1
fi

# Test 3: Get task by ID
if [ -n "${TASK_ID}" ]; then
    print_status "Test 3: Getting task by ID..."
    GET_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/api/tasks/${TASK_ID} 2>/dev/null || echo "000")

    if [ "${GET_RESPONSE}" == "200" ]; then
        print_success "Task retrieved successfully"
    else
        print_error "Failed to retrieve task (HTTP ${GET_RESPONSE})"
        FAILED=1
    fi

    # Test 4: Update task
    print_status "Test 4: Updating task..."
    UPDATE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH ${API_URL}/api/tasks/${TASK_ID} \
        -H "Content-Type: application/json" \
        -d '{"title":"Updated Test Task"}' 2>/dev/null || echo "000")

    if [ "${UPDATE_RESPONSE}" == "200" ]; then
        print_success "Task updated successfully"
    else
        print_error "Failed to update task (HTTP ${UPDATE_RESPONSE})"
        FAILED=1
    fi

    # Test 5: Complete task
    print_status "Test 5: Completing task..."
    COMPLETE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST ${API_URL}/api/tasks/${TASK_ID}/complete 2>/dev/null || echo "000")

    if [ "${COMPLETE_RESPONSE}" == "200" ] || [ "${COMPLETE_RESPONSE}" == "204" ]; then
        print_success "Task completed successfully"
    else
        print_error "Failed to complete task (HTTP ${COMPLETE_RESPONSE})"
        FAILED=1
    fi
fi

# Step 5: Event-driven features
print_status "Step 5: Validating event-driven features..."

# Check Dapr pub/sub components
if kubectl get component kafka-pubsub -n ${NAMESPACE} &>/dev/null; then
    print_success "Kafka pub/sub component configured"
else
    print_warning "Kafka pub/sub component not found"
fi

# Check subscriptions
SUBSCRIPTIONS=$(kubectl get subscription -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l)
if [ ${SUBSCRIPTIONS} -gt 0 ]; then
    print_success "Event subscriptions configured (${SUBSCRIPTIONS} subscriptions)"
else
    print_warning "No event subscriptions found"
fi

# Step 6: Monitoring and observability
print_status "Step 6: Checking monitoring setup..."

if kubectl get servicemonitor -n monitoring &>/dev/null; then
    SM_COUNT=$(kubectl get servicemonitor -n monitoring --no-headers | wc -l)
    print_success "Service monitors configured (${SM_COUNT} monitors)"
else
    print_warning "Service monitors not found"
fi

if kubectl get pod -n monitoring -l app.kubernetes.io/name=prometheus &>/dev/null; then
    print_success "Prometheus deployed"
else
    print_warning "Prometheus not deployed"
fi

if kubectl get pod -n monitoring -l app.kubernetes.io/name=grafana &>/dev/null; then
    print_success "Grafana deployed"
else
    print_warning "Grafana not deployed"
fi

# Step 7: Security checks
print_status "Step 7: Running security checks..."

# Check secrets
if kubectl get secret todo-app-secrets -n ${NAMESPACE} &>/dev/null; then
    print_success "Application secrets configured"
else
    print_error "Application secrets not found"
    FAILED=1
fi

# Check pod security
NON_ROOT=$(kubectl get pods -n ${NAMESPACE} -o jsonpath='{.items[*].spec.containers[*].securityContext.runAsNonRoot}' 2>/dev/null | grep -c "true" || echo "0")

if [ ${NON_ROOT} -gt 0 ]; then
    print_success "Pods running as non-root user"
else
    print_warning "Some pods may be running as root"
fi

# Step 8: Resilience configuration
print_status "Step 8: Checking resilience configuration..."

# Check HPA
if kubectl get hpa -n ${NAMESPACE} &>/dev/null; then
    HPA_COUNT=$(kubectl get hpa -n ${NAMESPACE} --no-headers | wc -l)
    print_success "Horizontal Pod Autoscaling configured (${HPA_COUNT} HPAs)"
else
    print_warning "HPA not configured"
fi

# Check PDB
if kubectl get pdb -n ${NAMESPACE} &>/dev/null; then
    PDB_COUNT=$(kubectl get pdb -n ${NAMESPACE} --no-headers | wc -l)
    print_success "Pod Disruption Budgets configured (${PDB_COUNT} PDBs)"
else
    print_warning "PDB not configured"
fi

# Check Dapr resiliency
if kubectl get resiliency -n ${NAMESPACE} &>/dev/null; then
    print_success "Dapr resiliency policies configured"
else
    print_warning "Dapr resiliency not configured"
fi

# Summary
echo ""
echo "========================================"
if [ ${FAILED} -eq 0 ]; then
    print_success "End-to-end validation PASSED!"
    print_status "All critical systems are functioning correctly"
    echo ""
    print_status "System is ready for production use"
    exit 0
else
    print_error "End-to-end validation FAILED!"
    print_status "Please address the errors above"
    exit 1
fi
