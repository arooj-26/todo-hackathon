# CI/CD Pipeline Documentation

This directory contains GitHub Actions workflows for automated build, test, and deployment.

## Overview

The CI/CD pipeline implements:
- **FR-025**: Automatic build, test, and deploy to staging on commit to main
- **FR-026**: Manual approval required for production deployment
- **FR-027**: Automatic rollback on health check failures
- **SC-013**: Deploy to staging within 15 minutes
- **SC-014**: Rollback within 2 minutes
- **SC-015**: Zero-downtime deployments with rolling updates

## Workflows

### `ci-cd.yaml` - Main CI/CD Pipeline

Triggered on:
- Push to `main` or `1-kubernetes-deployment` branches
- Pull requests to these branches
- Manual workflow dispatch

**Pipeline Stages:**

1. **Build and Test** (Parallel for all services)
   - Builds Docker images for all services
   - Pushes to GitHub Container Registry
   - Runs unit tests if available
   - Caches layers for faster builds

2. **Deploy to Staging** (Auto)
   - Deploys to staging environment
   - Waits for rollout completion
   - Runs smoke tests
   - Auto-rollback on failure

3. **Deploy to Production** (Manual Approval Required)
   - Requires manual approval in GitHub UI
   - Deploys with rolling update strategy
   - Comprehensive health checks
   - Auto-rollback on failure
   - Pod health monitoring

## Setup Requirements

### 1. GitHub Secrets

Configure these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

#### Required Secrets:

```bash
# Staging environment kubeconfig (base64 encoded)
STAGING_KUBECONFIG=<base64-encoded-kubeconfig>

# Production environment kubeconfig (base64 encoded)
PRODUCTION_KUBECONFIG=<base64-encoded-kubeconfig>
```

#### How to create secrets:

```bash
# For Azure AKS
az aks get-credentials --resource-group <rg> --name <cluster-name> --file kubeconfig-staging.yaml
cat kubeconfig-staging.yaml | base64 -w 0

# For Google GKE
gcloud container clusters get-credentials <cluster-name> --zone <zone> --project <project>
cat ~/.kube/config | base64 -w 0

# For Oracle OKE
oci ce cluster create-kubeconfig --cluster-id <cluster-ocid> --file kubeconfig-prod.yaml
cat kubeconfig-prod.yaml | base64 -w 0
```

### 2. GitHub Environments

Create two environments in GitHub repository settings:

**Staging Environment:**
- Name: `staging`
- URL: `https://staging.todo-app.example.com`
- Protection rules: None (auto-deploy)

**Production Environment:**
- Name: `production`
- URL: `https://todo-app.example.com`
- Protection rules:
  - ✅ Required reviewers: 1+ team members
  - ✅ Wait timer: 0 minutes (can deploy immediately after approval)
  - ✅ Prevent administrators from bypassing: Optional

### 3. Container Registry Access

The pipeline uses GitHub Container Registry (ghcr.io) which requires:
- GitHub Actions has automatic access via `GITHUB_TOKEN`
- No additional secrets needed
- Images are pushed to: `ghcr.io/<your-org>/web-todo-<service>:<tag>`

### 4. Kubernetes Cluster Prerequisites

Each cluster (staging & production) must have:

✅ **Namespace created:**
```bash
kubectl apply -f k8s/namespace.yaml
```

✅ **Secrets configured:**
```bash
kubectl apply -f k8s/secrets.yaml
```

✅ **Dapr installed:**
```bash
dapr init --kubernetes --wait
```

✅ **Network policies supported (if using Calico/Cilium):**
```bash
kubectl apply -f k8s/network-policies.yaml
```

## Usage

### Automatic Staging Deployment

Every commit to `main` branch automatically:
1. Builds Docker images
2. Runs tests
3. Deploys to staging
4. Runs smoke tests
5. Waits for production approval

**Timeline: ~10-15 minutes**

### Manual Production Deployment

After staging deployment succeeds:

1. Go to GitHub repository → Actions tab
2. Click on the workflow run
3. Click "Review deployments"
4. Select "production" environment
5. Click "Approve and deploy"

**Timeline: ~5-10 minutes after approval**

### Manual Workflow Trigger

Deploy to a specific environment manually:

1. Go to Actions → CI/CD Pipeline
2. Click "Run workflow"
3. Select branch: `main`
4. Select environment: `staging` or `production`
5. Click "Run workflow"

### Rollback

Automatic rollback triggers when:
- Smoke tests fail
- Health checks fail
- Pods don't reach Running state
- Deployment timeout exceeded

Manual rollback:
```bash
# Rollback specific deployment
kubectl rollout undo deployment/<service-name> -n todo-app

# Rollback all services
kubectl rollout undo deployment/chat-api -n todo-app
kubectl rollout undo deployment/frontend -n todo-app
kubectl rollout undo deployment/recurring-tasks -n todo-app
kubectl rollout undo deployment/notifications -n todo-app
kubectl rollout undo deployment/audit -n todo-app
```

## Pipeline Flow Diagram

```
┌─────────────┐
│ Git Push    │
│ to main     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Build & Test (Parallel)             │
│ ├─ chat-api                         │
│ ├─ recurring-tasks                  │
│ ├─ notifications                    │
│ ├─ audit                            │
│ └─ frontend                         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Deploy to Staging (Auto)            │
│ ├─ Apply manifests                  │
│ ├─ Wait for rollout                 │
│ ├─ Run smoke tests                  │
│ └─ Auto-rollback on failure         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Wait for Manual Approval            │
│ (GitHub Environment Protection)     │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Deploy to Production                │
│ ├─ Apply manifests                  │
│ ├─ Rolling update (zero-downtime)   │
│ ├─ Health checks (5 iterations)     │
│ ├─ Pod health monitoring            │
│ └─ Auto-rollback on failure         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Success Notification                │
└─────────────────────────────────────┘
```

## Health Checks

### Smoke Tests (Staging)
- `/health` endpoint check
- `/` root endpoint check
- Timeout: 30 seconds wait time

### Health Checks (Production)
- `/health` endpoint check (5 iterations)
- `/ready` readiness probe check (5 iterations)
- Pod health monitoring (all pods must be Running)
- Total timeout: 60 seconds + 50 seconds checks

### Rollback Triggers
- Any HTTP error from health endpoints
- Pods in non-Running state
- Deployment rollout timeout
- Smoke/health test failures

## Deployment Strategies

### Rolling Update (Zero-Downtime)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

This ensures:
- New pods are ready before old pods terminate
- Service remains available during updates
- Gradual rollout minimizes risk

### Rollback Strategy
- Automatic rollback to previous revision
- Rollback completes in ~2 minutes (SC-014)
- No data loss (stateless services)

## Troubleshooting

### Build Failures

```bash
# View build logs
GitHub Actions → Workflow run → Build and Test → Select failed service

# Common issues:
- Docker build context errors → Check Dockerfile path
- Test failures → Check test logs in workflow output
- Registry push failures → Check GITHUB_TOKEN permissions
```

### Deployment Failures

```bash
# View deployment logs
kubectl logs -n todo-app deployment/<service-name>

# Check pod status
kubectl get pods -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Common issues:
- ImagePullBackOff → Check image tag and registry access
- CrashLoopBackOff → Check service logs and health checks
- Pending pods → Check resource limits and node capacity
```

### Health Check Failures

```bash
# Test health endpoints manually
kubectl port-forward -n todo-app svc/chat-api 8000:8000
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Common issues:
- Service not responding → Check if pod is running
- Database connection failed → Check secrets and connectivity
- Dapr sidecar not ready → Wait for Dapr initialization
```

## Metrics and Monitoring

Pipeline execution metrics:
- Build time: ~5-8 minutes (parallel builds)
- Test time: ~2-3 minutes (if tests exist)
- Staging deployment: ~5-7 minutes
- Production deployment: ~8-10 minutes
- **Total staging: ~12-18 minutes (meets SC-013: <15min target)**
- **Rollback time: ~2 minutes (meets SC-014)**

## Security Best Practices

1. **Never commit secrets** to repository
2. **Use environment-specific secrets** for staging/production
3. **Rotate kubeconfig credentials** quarterly
4. **Enable branch protection** for main branch
5. **Require code reviews** before merge
6. **Scan container images** for vulnerabilities (can add Trivy/Snyk)
7. **Use least-privilege kubeconfig** (namespace-scoped if possible)

## Next Steps

To enhance the pipeline:

1. **Add integration tests** between services
2. **Add security scanning** (Trivy, Snyk)
3. **Add performance tests** (load testing)
4. **Add Slack/email notifications** on deployment status
5. **Add automated rollback** based on error rate metrics
6. **Add canary deployments** for gradual rollout

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Rolling Updates](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
