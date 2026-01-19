#!/bin/bash
# Script to apply critical security and functionality fixes
# Run this script from the project root: bash k8s/scripts/apply-critical-fixes.sh

set -e  # Exit on error

echo "========================================="
echo "Applying Critical Fixes to Todo App"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if namespace exists
echo "Checking namespace..."
if ! kubectl get namespace todo-app &> /dev/null; then
    echo -e "${YELLOW}Namespace 'todo-app' not found. Creating...${NC}"
    kubectl create namespace todo-app
fi

echo -e "${GREEN}✓ Namespace ready${NC}"
echo ""

# Step 1: Apply secrets
echo "Step 1: Applying Kubernetes Secrets..."
echo -e "${YELLOW}⚠️  IMPORTANT: Edit k8s/secrets.yaml and replace placeholder values!${NC}"
echo "   - JWT_SECRET: Must match Phase-4 auth backend"
echo "   - Database password: Use secure password in production"
echo "   - SMTP credentials: Add your email server details"
echo ""
read -p "Have you updated the secrets? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}✗ Please update k8s/secrets.yaml first, then re-run this script${NC}"
    exit 1
fi

kubectl apply -f k8s/secrets.yaml
echo -e "${GREEN}✓ Secrets applied${NC}"
echo ""

# Step 2: Rebuild chat-api Docker image (includes CORS fix and user sync)
echo "Step 2: Rebuilding chat-api Docker image with fixes..."
eval $(minikube docker-env)

cd phase-5/services/chat-api
docker build -t phase-5-chat-api:latest .
cd ../../..

echo -e "${GREEN}✓ chat-api image rebuilt${NC}"
echo ""

# Step 3: Apply updated deployment manifests
echo "Step 3: Applying updated Kubernetes deployments..."
kubectl apply -f k8s/simple-deploy.yaml
echo -e "${GREEN}✓ Deployments updated${NC}"
echo ""

# Step 4: Restart affected pods
echo "Step 4: Restarting affected deployments..."
kubectl rollout restart deployment/postgres -n todo-app
kubectl rollout restart deployment/chat-api -n todo-app

echo "Waiting for rollout to complete..."
kubectl rollout status deployment/postgres -n todo-app
kubectl rollout status deployment/chat-api -n todo-app

echo -e "${GREEN}✓ Pods restarted${NC}"
echo ""

# Step 5: Verify deployment
echo "Step 5: Verifying deployment..."
echo ""

echo "Pod Status:"
kubectl get pods -n todo-app

echo ""
echo "Checking chat-api logs for CORS warning..."
kubectl logs -n todo-app -l app=chat-api -c chat-api --tail=20 | grep -i cors || echo "No CORS warnings found (good!)"

echo ""
echo "========================================="
echo "Critical Fixes Applied Successfully! ✓"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Test authentication: User should auto-sync from Phase-4 on first login"
echo "2. Verify CORS: Check that only whitelisted origins can access API"
echo "3. Test database connection: Ensure secrets are working"
echo ""
echo "To test:"
echo "  Frontend: http://$(minikube ip):30000"
echo "  Chat API: http://$(minikube ip):32162"
echo ""
echo "Check logs:"
echo "  kubectl logs -n todo-app -l app=chat-api -c chat-api -f"
echo ""
