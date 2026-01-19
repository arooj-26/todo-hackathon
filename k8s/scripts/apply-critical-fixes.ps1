# PowerShell script to apply critical security and functionality fixes
# Run this script from the project root: .\k8s\scripts\apply-critical-fixes.ps1

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Applying Critical Fixes to Todo App" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if namespace exists
Write-Host "Checking namespace..." -ForegroundColor Yellow
try {
    kubectl get namespace todo-app 2>&1 | Out-Null
    Write-Host "✓ Namespace exists" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Namespace 'todo-app' not found. Creating..." -ForegroundColor Yellow
    kubectl create namespace todo-app
    Write-Host "✓ Namespace created" -ForegroundColor Green
}
Write-Host ""

# Step 1: Apply secrets
Write-Host "Step 1: Applying Kubernetes Secrets..." -ForegroundColor Cyan
Write-Host "⚠️  IMPORTANT: Edit k8s/secrets.yaml and replace placeholder values!" -ForegroundColor Yellow
Write-Host "   - JWT_SECRET: Must match Phase-4 auth backend"
Write-Host "   - Database password: Use secure password in production"
Write-Host "   - SMTP credentials: Add your email server details"
Write-Host ""

$confirmation = Read-Host "Have you updated the secrets? (y/n)"
if ($confirmation -ne 'y') {
    Write-Host "✗ Please update k8s/secrets.yaml first, then re-run this script" -ForegroundColor Red
    exit 1
}

kubectl apply -f k8s/secrets.yaml
Write-Host "✓ Secrets applied" -ForegroundColor Green
Write-Host ""

# Step 2: Rebuild chat-api Docker image
Write-Host "Step 2: Rebuilding chat-api Docker image with fixes..." -ForegroundColor Cyan
& minikube docker-env --shell powershell | Invoke-Expression

Push-Location phase-5/services/chat-api
docker build -t phase-5-chat-api:latest .
Pop-Location

Write-Host "✓ chat-api image rebuilt" -ForegroundColor Green
Write-Host ""

# Step 3: Apply updated deployment manifests
Write-Host "Step 3: Applying updated Kubernetes deployments..." -ForegroundColor Cyan
kubectl apply -f k8s/simple-deploy.yaml
Write-Host "✓ Deployments updated" -ForegroundColor Green
Write-Host ""

# Step 4: Restart affected pods
Write-Host "Step 4: Restarting affected deployments..." -ForegroundColor Cyan
kubectl rollout restart deployment/postgres -n todo-app
kubectl rollout restart deployment/chat-api -n todo-app

Write-Host "Waiting for rollout to complete..."
kubectl rollout status deployment/postgres -n todo-app
kubectl rollout status deployment/chat-api -n todo-app

Write-Host "✓ Pods restarted" -ForegroundColor Green
Write-Host ""

# Step 5: Verify deployment
Write-Host "Step 5: Verifying deployment..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Pod Status:" -ForegroundColor Yellow
kubectl get pods -n todo-app

Write-Host ""
Write-Host "Checking chat-api logs for CORS warning..." -ForegroundColor Yellow
$logs = kubectl logs -n todo-app -l app=chat-api -c chat-api --tail=20 2>&1
if ($logs -match "CORS") {
    Write-Host $logs -ForegroundColor Yellow
} else {
    Write-Host "No CORS warnings found (good!)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Critical Fixes Applied Successfully! ✓" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test authentication: User should auto-sync from Phase-4 on first login"
Write-Host "2. Verify CORS: Check that only whitelisted origins can access API"
Write-Host "3. Test database connection: Ensure secrets are working"
Write-Host ""
$minikubeIp = minikube ip
Write-Host "To test:" -ForegroundColor Yellow
Write-Host "  Frontend: http://${minikubeIp}:30000"
Write-Host "  Chat API: http://${minikubeIp}:32162"
Write-Host ""
Write-Host "Check logs:" -ForegroundColor Yellow
Write-Host "  kubectl logs -n todo-app -l app=chat-api -c chat-api -f"
Write-Host ""
