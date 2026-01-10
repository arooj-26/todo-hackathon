#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

FAILED=0

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Todo App - Deployment Validation${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""

# Function to check if pods are running
check_pods() {
    local namespace=$1
    local label=$2
    local expected_count=$3

    echo -e "${YELLOW}Checking pods in namespace '$namespace' with label '$label'...${NC}"

    local running_count=$(kubectl get pods -n $namespace -l $label --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)

    if [ "$running_count" -eq "$expected_count" ]; then
        echo -e "${GREEN}✓ $running_count/$expected_count pods are running${NC}"
        return 0
    else
        echo -e "${RED}✗ Only $running_count/$expected_count pods are running${NC}"
        kubectl get pods -n $namespace -l $label
        return 1
    fi
}

# Function to check if service is accessible
check_service() {
    local service_name=$1
    local namespace=$2
    local port=$3

    echo -e "${YELLOW}Checking service '$service_name' in namespace '$namespace'...${NC}"

    if kubectl get svc $service_name -n $namespace &> /dev/null; then
        echo -e "${GREEN}✓ Service '$service_name' exists${NC}"
        return 0
    else
        echo -e "${RED}✗ Service '$service_name' not found${NC}"
        FAILED=1
        return 1
    fi
}

# Function to check health endpoint
check_health() {
    local service_name=$1
    local namespace=$2
    local port=$3

    echo -e "${YELLOW}Checking health endpoint for '$service_name'...${NC}"

    # Get pod name
    local pod_name=$(kubectl get pods -n $namespace -l app=$service_name -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$pod_name" ]; then
        echo -e "${RED}✗ No pod found for service '$service_name'${NC}"
        FAILED=1
        return 1
    fi

    # Port forward and check health (with timeout)
    local health_response=$(kubectl exec -n $namespace $pod_name -- curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null || echo "000")

    if [ "$health_response" = "200" ]; then
        echo -e "${GREEN}✓ Health endpoint is responding (HTTP $health_response)${NC}"
        return 0
    else
        echo -e "${RED}✗ Health endpoint is not responding (HTTP $health_response)${NC}"
        FAILED=1
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Checking Dapr System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_pods "dapr-system" "app.kubernetes.io/name=dapr" 3 || FAILED=1
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Checking Kafka System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_pods "kafka" "app.kubernetes.io/name=entity-operator" 1 || FAILED=1
echo -e "${YELLOW}Checking Kafka cluster...${NC}"
if kubectl get kafka kafka-cluster -n kafka &> /dev/null; then
    local kafka_status=$(kubectl get kafka kafka-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    if [ "$kafka_status" = "True" ]; then
        echo -e "${GREEN}✓ Kafka cluster is ready${NC}"
    else
        echo -e "${RED}✗ Kafka cluster is not ready${NC}"
        FAILED=1
    fi
else
    echo -e "${RED}✗ Kafka cluster not found${NC}"
    FAILED=1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Checking PostgreSQL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_pods "todo-app" "app=postgres" 1 || FAILED=1
check_service "postgres-service" "todo-app" 5432 || FAILED=1
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Checking Todo App Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Chat API
check_pods "todo-app" "app=chat-api" 1 || FAILED=1
check_service "chat-api" "todo-app" 8000 || FAILED=1
check_health "chat-api" "todo-app" 8000 || true  # Don't fail if health check fails
echo ""

# Recurring Tasks
check_pods "todo-app" "app=recurring-tasks" 1 || FAILED=1
check_service "recurring-tasks" "todo-app" 8001 || FAILED=1
check_health "recurring-tasks" "todo-app" 8001 || true
echo ""

# Notifications
check_pods "todo-app" "app=notifications" 1 || FAILED=1
check_service "notifications" "todo-app" 8002 || FAILED=1
check_health "notifications" "todo-app" 8002 || true
echo ""

# Audit
check_pods "todo-app" "app=audit" 1 || FAILED=1
check_service "audit" "todo-app" 8003 || FAILED=1
check_health "audit" "todo-app" 8003 || true
echo ""

# Frontend
check_pods "todo-app" "app=frontend" 1 || FAILED=1
check_service "frontend" "todo-app" 3000 || FAILED=1
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Checking Dapr Components"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Dapr components
for component in kafka-pubsub statestore secretstore; do
    echo -e "${YELLOW}Checking Dapr component '$component'...${NC}"
    if kubectl get component $component -n todo-app &> /dev/null; then
        echo -e "${GREEN}✓ Dapr component '$component' exists${NC}"
    else
        echo -e "${RED}✗ Dapr component '$component' not found${NC}"
        FAILED=1
    fi
done
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validation checks passed!${NC}"
    echo ""

    MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "localhost")
    echo -e "${GREEN}Access the application:${NC}"
    echo -e "  Frontend:  http://$MINIKUBE_IP:30000"
    echo -e "  Chat API:  http://$MINIKUBE_IP:30080"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Access the frontend to test the application"
    echo "  2. Check logs: kubectl logs -n todo-app <pod-name>"
    echo "  3. Monitor with Dapr dashboard: dapr dashboard -k -n todo-app"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some validation checks failed${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Check pod logs:   kubectl logs -n todo-app <pod-name>"
    echo "  2. Describe pod:     kubectl describe pod -n todo-app <pod-name>"
    echo "  3. Check events:     kubectl get events -n todo-app --sort-by='.lastTimestamp'"
    echo "  4. Restart pod:      kubectl delete pod -n todo-app <pod-name>"
    echo ""
    exit 1
fi
