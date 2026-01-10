#!/bin/bash
# Validate deployment gates from constitution
# Ensures proper progression: local → staging → production

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

ENVIRONMENT="${1:-staging}"
NAMESPACE="${NAMESPACE:-todo-app}"

print_status "Validating deployment gates for environment: ${ENVIRONMENT}"
echo ""

# Gate 1: All pods must be running
print_status "Gate 1: Checking pod health..."
TOTAL_PODS=$(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l)
RUNNING_PODS=$(kubectl get pods -n ${NAMESPACE} --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)

if [ ${RUNNING_PODS} -eq ${TOTAL_PODS} ] && [ ${TOTAL_PODS} -gt 0 ]; then
    print_success "All ${TOTAL_PODS} pods are running"
else
    print_error "Only ${RUNNING_PODS}/${TOTAL_PODS} pods are running"
    exit 1
fi

# Gate 2: All health endpoints must respond
print_status "Gate 2: Checking health endpoints..."
SERVICES=("chat-api" "recurring-tasks" "notifications" "audit" "frontend")
HEALTH_FAILED=0

for service in "${SERVICES[@]}"; do
    POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$POD" ]; then
        print_error "${service}: No pod found"
        HEALTH_FAILED=1
        continue
    fi

    case ${service} in
        chat-api) PORT=8000 ;;
        recurring-tasks) PORT=8001 ;;
        notifications) PORT=8002 ;;
        audit) PORT=8003 ;;
        frontend) PORT=3000; HEALTH_PATH="/" ;;
    esac

    HEALTH_PATH="${HEALTH_PATH:-/health}"

    STATUS=$(kubectl exec ${POD} -n ${NAMESPACE} -c ${service} -- curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}${HEALTH_PATH} 2>/dev/null || echo "000")

    if [ "${STATUS}" == "200" ]; then
        print_success "${service}: Health check passed"
    else
        print_error "${service}: Health check failed (HTTP ${STATUS})"
        HEALTH_FAILED=1
    fi
done

if [ ${HEALTH_FAILED} -eq 1 ]; then
    exit 1
fi

# Gate 3: Database connectivity
print_status "Gate 3: Checking database connectivity..."
POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=chat-api -o jsonpath='{.items[0].metadata.name}')
DB_CHECK=$(kubectl exec ${POD} -n ${NAMESPACE} -c chat-api -- python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    conn.close()
    print('success')
except Exception as e:
    print(f'failed: {e}')
" 2>/dev/null || echo "failed: command failed")

if [[ "${DB_CHECK}" == "success" ]]; then
    print_success "Database connectivity verified"
else
    print_error "Database connectivity failed: ${DB_CHECK}"
    exit 1
fi

# Gate 4: Kafka connectivity (if applicable)
if kubectl get kafka kafka-cluster -n kafka &>/dev/null; then
    print_status "Gate 4: Checking Kafka connectivity..."
    KAFKA_STATUS=$(kubectl get kafka kafka-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)

    if [ "${KAFKA_STATUS}" == "True" ]; then
        print_success "Kafka cluster is ready"
    else
        print_error "Kafka cluster is not ready"
        exit 1
    fi
else
    print_warning "Gate 4: Kafka not deployed (skipping)"
fi

# Gate 5: Dapr sidecars running
print_status "Gate 5: Checking Dapr sidecars..."
DAPR_FAILED=0

for service in "chat-api" "recurring-tasks" "notifications" "audit"; do
    POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=${service} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$POD" ]; then
        continue
    fi

    CONTAINER_COUNT=$(kubectl get pod ${POD} -n ${NAMESPACE} -o jsonpath='{.spec.containers[*].name}' 2>/dev/null | wc -w)

    if [ ${CONTAINER_COUNT} -ge 2 ]; then
        print_success "${service}: Dapr sidecar present"
    else
        print_error "${service}: Dapr sidecar missing"
        DAPR_FAILED=1
    fi
done

if [ ${DAPR_FAILED} -eq 1 ]; then
    exit 1
fi

# Gate 6: No crash loops
print_status "Gate 6: Checking for crash loops..."
CRASH_LOOPS=$(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | awk '{if ($4 > 2) print $1 " (" $4 " restarts)"}')

if [ -z "${CRASH_LOOPS}" ]; then
    print_success "No crash loops detected"
else
    print_error "Crash loops detected:"
    echo "${CRASH_LOOPS}"
    exit 1
fi

# Gate 7: Resource usage within limits
print_status "Gate 7: Checking resource usage..."
RESOURCE_WARNINGS=0

while IFS= read -r line; do
    POD=$(echo ${line} | awk '{print $1}')
    CPU=$(echo ${line} | awk '{print $2}' | sed 's/m//')
    MEMORY=$(echo ${line} | awk '{print $3}' | sed 's/Mi//')

    # Check if CPU > 90% of limit (assuming 1000m limit)
    if [ ${CPU} -gt 900 ]; then
        print_warning "${POD}: High CPU usage (${CPU}m)"
        RESOURCE_WARNINGS=1
    fi

    # Check if memory > 90% of limit (assuming 1024Mi limit)
    if [ ${MEMORY} -gt 921 ]; then
        print_warning "${POD}: High memory usage (${MEMORY}Mi)"
        RESOURCE_WARNINGS=1
    fi
done < <(kubectl top pods -n ${NAMESPACE} --no-headers 2>/dev/null || echo "")

if [ ${RESOURCE_WARNINGS} -eq 0 ]; then
    print_success "Resource usage within acceptable limits"
fi

# Gate 8: Secrets not in source code
print_status "Gate 8: Verifying secrets management..."
if kubectl get secret todo-app-secrets -n ${NAMESPACE} &>/dev/null; then
    print_success "Secrets configured via Kubernetes Secrets"
else
    print_error "Secrets not properly configured"
    exit 1
fi

# Environment-specific gates
if [ "${ENVIRONMENT}" == "production" ]; then
    print_status "Production-specific gates..."

    # Gate 9: Monitoring enabled
    if kubectl get servicemonitor -n monitoring &>/dev/null; then
        print_success "Monitoring is enabled"
    else
        print_error "Monitoring not enabled (required for production)"
        exit 1
    fi

    # Gate 10: Ingress configured
    if kubectl get ingress -n ${NAMESPACE} &>/dev/null; then
        print_success "Ingress is configured"
    else
        print_error "Ingress not configured (required for production)"
        exit 1
    fi

    # Gate 11: HPA enabled
    if kubectl get hpa -n ${NAMESPACE} &>/dev/null; then
        print_success "Horizontal Pod Autoscaling is enabled"
    else
        print_warning "HPA not enabled (recommended for production)"
    fi

    # Gate 12: PDB configured
    if kubectl get pdb -n ${NAMESPACE} &>/dev/null; then
        print_success "Pod Disruption Budgets are configured"
    else
        print_warning "PDB not configured (recommended for production)"
    fi
fi

echo ""
print_success "All deployment gates passed for ${ENVIRONMENT}!"
echo ""
print_status "Deployment is ready for the next stage"
