#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Todo App - Rollback Utility${NC}"
echo -e "${GREEN}======================================${NC}"

# Default values
NAMESPACE="${NAMESPACE:-todo-app}"
RELEASE_NAME="${RELEASE_NAME:-todo-app}"
REVISION=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    -r|--revision)
      REVISION="$2"
      shift 2
      ;;
    --release)
      RELEASE_NAME="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  -n, --namespace NAMESPACE    Kubernetes namespace (default: todo-app)"
      echo "  -r, --revision REVISION      Revision number to rollback to"
      echo "      --release RELEASE        Helm release name (default: todo-app)"
      echo "  -h, --help                   Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0                           # Rollback to previous revision"
      echo "  $0 -r 3                      # Rollback to revision 3"
      echo "  $0 -n production -r 5        # Rollback production namespace to revision 5"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use -h or --help for usage information"
      exit 1
      ;;
  esac
done

# Check if helm is installed
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm is not installed${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl is not installed${NC}"; exit 1; }

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${RED}Error: Namespace '$NAMESPACE' does not exist${NC}"
    exit 1
fi

# Check if Helm release exists
if ! helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
    echo -e "${RED}Error: Helm release '$RELEASE_NAME' not found in namespace '$NAMESPACE'${NC}"
    exit 1
fi

echo -e "${YELLOW}Current deployment status:${NC}"
echo ""

# Show current revision
CURRENT_REVISION=$(helm list -n $NAMESPACE | grep $RELEASE_NAME | awk '{print $3}')
echo -e "Current revision: ${GREEN}$CURRENT_REVISION${NC}"
echo ""

# Show revision history
echo -e "${YELLOW}Revision history:${NC}"
helm history $RELEASE_NAME -n $NAMESPACE

echo ""

# Determine target revision
if [ -z "$REVISION" ]; then
    TARGET_REVISION=$((CURRENT_REVISION - 1))
    echo -e "${YELLOW}No revision specified. Will rollback to previous revision: $TARGET_REVISION${NC}"
else
    TARGET_REVISION=$REVISION
    echo -e "${YELLOW}Will rollback to revision: $TARGET_REVISION${NC}"
fi

# Validate target revision exists
if ! helm history $RELEASE_NAME -n $NAMESPACE | grep -q "^\s*$TARGET_REVISION\s"; then
    echo -e "${RED}Error: Revision $TARGET_REVISION does not exist${NC}"
    echo "Available revisions:"
    helm history $RELEASE_NAME -n $NAMESPACE
    exit 1
fi

echo ""
echo -e "${YELLOW}Pre-rollback checks:${NC}"

# Check current pod status
echo -e "${YELLOW}Current pod status:${NC}"
kubectl get pods -n $NAMESPACE -l "app in (chat-api,recurring-tasks,notifications,audit,frontend)"

echo ""
read -p "Do you want to proceed with rollback? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Rollback cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Starting rollback...${NC}"

# Perform rollback
helm rollback $RELEASE_NAME $TARGET_REVISION -n $NAMESPACE --wait

echo ""
echo -e "${GREEN}Rollback completed!${NC}"

# Show new status
echo ""
echo -e "${YELLOW}Post-rollback status:${NC}"

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l "app in (chat-api,recurring-tasks,notifications,audit,frontend)" \
  -n $NAMESPACE --timeout=300s || true

# Show pod status
echo ""
echo -e "${YELLOW}Pod status:${NC}"
kubectl get pods -n $NAMESPACE -l "app in (chat-api,recurring-tasks,notifications,audit,frontend)"

# Show service status
echo ""
echo -e "${YELLOW}Service status:${NC}"
kubectl get svc -n $NAMESPACE

# Show Helm release status
echo ""
echo -e "${YELLOW}Helm release status:${NC}"
helm status $RELEASE_NAME -n $NAMESPACE

# Health check
echo ""
echo -e "${YELLOW}Running health checks...${NC}"

FAILED_CHECKS=0

for service in chat-api recurring-tasks notifications audit; do
    POD=$(kubectl get pods -n $NAMESPACE -l app=$service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

    if [ -z "$POD" ]; then
        echo -e "${RED}✗ $service: No pod found${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        continue
    fi

    # Check if pod is running
    POD_STATUS=$(kubectl get pod $POD -n $NAMESPACE -o jsonpath='{.status.phase}')
    if [ "$POD_STATUS" != "Running" ]; then
        echo -e "${RED}✗ $service: Pod not running (status: $POD_STATUS)${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        continue
    fi

    # Check health endpoint
    HEALTH_STATUS=$(kubectl exec -n $NAMESPACE $POD -- curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")

    if [ "$HEALTH_STATUS" = "200" ]; then
        echo -e "${GREEN}✓ $service: Healthy${NC}"
    else
        echo -e "${RED}✗ $service: Health check failed (HTTP $HEALTH_STATUS)${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
done

echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}Rollback successful!${NC}"
    echo -e "${GREEN}All services are healthy${NC}"
    echo -e "${GREEN}======================================${NC}"
    exit 0
else
    echo -e "${RED}======================================${NC}"
    echo -e "${RED}Rollback completed with issues${NC}"
    echo -e "${RED}$FAILED_CHECKS health check(s) failed${NC}"
    echo -e "${RED}======================================${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Check pod logs: kubectl logs -n $NAMESPACE <pod-name>"
    echo "  2. Describe pod: kubectl describe pod -n $NAMESPACE <pod-name>"
    echo "  3. Check events: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    echo "  4. Consider rolling back to an earlier revision"
    echo ""
    exit 1
fi
