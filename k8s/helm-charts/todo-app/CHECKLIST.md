# Deployment Verification Checklist

Use this checklist to verify a successful deployment of the Todo App to Kubernetes.

## Pre-Deployment Verification

### Prerequisites
- [ ] Docker 4.53+ installed and running
- [ ] Minikube 1.32+ installed
- [ ] kubectl 1.28+ installed
- [ ] Helm 3.13+ installed (optional)
- [ ] Minimum 4 CPU cores and 8GB RAM available
- [ ] OpenAI API key obtained and configured

### Minikube Cluster
- [ ] Minikube cluster started successfully
- [ ] Minikube status shows all components running
- [ ] Metrics-server addon enabled
- [ ] Docker environment configured for Minikube (`eval $(minikube docker-env)`)

### Docker Images
- [ ] All 4 images built successfully:
  - [ ] `todo-backend:v1` (should be < 500MB)
  - [ ] `todo-frontend:v1` (should be < 500MB)
  - [ ] `chatbot-backend:v1` (should be < 500MB)
  - [ ] `chatbot-frontend:v1` (should be < 500MB)
- [ ] Images available in Minikube Docker daemon
- [ ] All images use non-root users
- [ ] All images use multi-stage builds

### Configuration
- [ ] `values.yaml` updated with actual secrets
- [ ] PostgreSQL password set (non-default)
- [ ] JWT secret key configured
- [ ] OpenAI API key configured
- [ ] Secrets NOT committed to version control

## Deployment Verification

### Kubernetes Resources Created
- [ ] ConfigMap `app-config` created
- [ ] Secret `app-secrets` created
- [ ] PersistentVolumeClaim `postgres-pvc` created (5Gi)
- [ ] All 5 Deployments created:
  - [ ] postgresql
  - [ ] todo-backend
  - [ ] todo-frontend
  - [ ] chatbot-backend
  - [ ] chatbot-frontend
- [ ] All 6 Services created:
  - [ ] postgresql (ClusterIP)
  - [ ] todo-backend (ClusterIP)
  - [ ] todo-frontend (NodePort :30000)
  - [ ] chatbot-backend (ClusterIP)
  - [ ] chatbot-frontend (NodePort :30001)
  - [ ] kubernetes (ClusterIP) - default service

### Pod Status
- [ ] All 7 pods in Running status:
  - [ ] 1x postgresql pod
  - [ ] 1x todo-backend pod
  - [ ] 2x todo-frontend pods
  - [ ] 1x chatbot-backend pod
  - [ ] 2x chatbot-frontend pods
- [ ] All pods show READY 1/1 (or 2/2 for frontends)
- [ ] No pods in CrashLoopBackOff status
- [ ] No pods in ImagePullBackOff status
- [ ] All pods have restarted < 5 times (excluding intentional restarts)

### Service Health
- [ ] All services have endpoints assigned
- [ ] PostgreSQL accepting connections on port 5432
- [ ] Todo backend responding on port 8000
- [ ] Todo frontend responding on port 3000
- [ ] Chatbot backend responding on port 8001
- [ ] Chatbot frontend responding on port 3001

### Database
- [ ] PostgreSQL pod logs show "database system is ready to accept connections"
- [ ] Database `todoapp` exists
- [ ] Can connect to PostgreSQL from backend pods
- [ ] PersistentVolumeClaim bound successfully
- [ ] Database data persists after pod restarts

### Backend Services
- [ ] Todo backend `/health` endpoint returns 200 OK
- [ ] Todo backend health response: `{"status":"healthy"}`
- [ ] Chatbot backend `/health` endpoint returns 200 OK
- [ ] Chatbot backend health response includes service name and version
- [ ] Backend logs show no critical errors
- [ ] Backends can connect to PostgreSQL
- [ ] Backends have correct environment variables set

### Frontend Services
- [ ] Todo frontend accessible via NodePort 30000
- [ ] Todo frontend loads without JavaScript errors
- [ ] Todo frontend can reach todo-backend API
- [ ] Chatbot frontend accessible via NodePort 30001
- [ ] Chatbot frontend loads without JavaScript errors
- [ ] Chatbot frontend can reach chatbot-backend API

## Functional Testing

### Todo Application
- [ ] Can create a new task via UI
- [ ] Created task appears in task list
- [ ] Can mark task as complete
- [ ] Task status updates correctly
- [ ] Can delete a task
- [ ] Deleted task removed from list
- [ ] Tasks persist after browser refresh
- [ ] No console errors in browser

### Chatbot Application
- [ ] Chatbot UI loads and shows input field
- [ ] Can send a message to chatbot
- [ ] Chatbot responds to messages
- [ ] Can create tasks via chatbot ("Add task: Meeting")
- [ ] Tasks created via chatbot appear in Todo app
- [ ] Can list tasks via chatbot ("Show my tasks")
- [ ] Can delete tasks via chatbot
- [ ] No console errors in browser

### Data Persistence
- [ ] Create a task via Todo UI
- [ ] Delete todo-backend pod: `kubectl delete pod -l app=todo-backend`
- [ ] Wait for pod to auto-restart
- [ ] Task still exists after restart
- [ ] Data persisted in PostgreSQL PVC

### Inter-Service Communication
- [ ] Todo frontend can call todo-backend API
- [ ] Chatbot frontend can call chatbot-backend API
- [ ] Chatbot backend can call todo-backend API
- [ ] Both backends can access PostgreSQL
- [ ] Services resolve each other by DNS names

## Resource Verification

### Resource Usage
- [ ] Run `kubectl top pods` - all pods show CPU/Memory usage
- [ ] No pod exceeding CPU limits (500m max)
- [ ] No pod exceeding memory limits:
  - Frontends: < 512Mi
  - Backends: < 512Mi
  - PostgreSQL: < 1024Mi
- [ ] Run `kubectl top nodes` - Minikube has available resources
- [ ] Node CPU usage < 80%
- [ ] Node memory usage < 80%

### Resource Allocation
- [ ] All pods have resource requests defined
- [ ] All pods have resource limits defined
- [ ] Requests are reasonable for workload
- [ ] Limits prevent resource exhaustion

## Scaling & High Availability

### Scaling Test
- [ ] Scale todo-backend: `kubectl scale deployment todo-backend --replicas=2`
- [ ] Both todo-backend pods reach Running status
- [ ] Application still works with 2 backend replicas
- [ ] Scale back: `kubectl scale deployment todo-backend --replicas=1`
- [ ] Application still works after scaling down

### High Availability
- [ ] Multiple frontend replicas (2x todo-frontend, 2x chatbot-frontend)
- [ ] Frontend traffic distributed across replicas
- [ ] Can handle frontend pod failure gracefully
- [ ] Service continues with remaining pods

## Security Checks

### Pod Security
- [ ] All application containers run as non-root user
- [ ] No containers use privileged mode
- [ ] Secrets mounted securely (not in plain text)
- [ ] No hardcoded credentials in code or configs

### Network Security
- [ ] Backend services use ClusterIP (not exposed externally)
- [ ] Only frontends exposed via NodePort
- [ ] PostgreSQL not exposed outside cluster
- [ ] Secrets stored in Kubernetes Secrets (base64 encoded)

### Secret Management
- [ ] `.gitignore` excludes `values-*.yaml`
- [ ] Actual secrets NOT committed to Git
- [ ] OpenAI API key stored in Secret
- [ ] PostgreSQL password stored in Secret
- [ ] JWT secret key stored in Secret

## Observability

### Logging
- [ ] Can view logs from any pod
- [ ] Logs show appropriate detail level
- [ ] No excessive error/warning logs
- [ ] Logs include timestamps
- [ ] Health check logs appear regularly

### Monitoring
- [ ] Metrics-server collecting pod metrics
- [ ] Can view resource usage via `kubectl top`
- [ ] Readiness probes configured for all services
- [ ] Liveness probes configured for all services

### Events
- [ ] No critical events: `kubectl get events | grep -i error`
- [ ] Recent events show normal operations
- [ ] No repeated warning events

## Documentation

### Documentation Completeness
- [ ] README.md exists and is comprehensive
- [ ] TROUBLESHOOTING.md provides solutions to common issues
- [ ] CHECKLIST.md (this file) available for verification
- [ ] Architecture diagram included
- [ ] Configuration reference documented

### Operational Docs
- [ ] Deployment instructions clear and complete
- [ ] Scaling procedures documented
- [ ] Rollback procedures documented
- [ ] Cleanup/uninstall instructions provided

## Cleanup Verification (Post-Testing)

### Optional: Clean Uninstall
- [ ] Delete all resources: `kubectl delete -f k8s/rendered/`
- [ ] Verify all pods deleted
- [ ] Verify all services deleted
- [ ] Verify PVC deleted (or retained if desired)
- [ ] Stop Minikube: `minikube stop`
- [ ] Delete cluster: `minikube delete` (if needed)

---

## Quick Verification Commands

```bash
# Check all resources
kubectl get all

# Check pod status
kubectl get pods

# Check services and endpoints
kubectl get svc,endpoints

# Check resource usage
kubectl top pods
kubectl top nodes

# Test health endpoints
kubectl exec $(kubectl get pod -l app=todo-frontend -o name | head -1) -- \
  wget -qO- http://todo-backend:8000/health

kubectl exec $(kubectl get pod -l app=chatbot-frontend -o name | head -1) -- \
  wget -qO- http://chatbot-backend:8001/health

# View logs
kubectl logs -l app=todo-backend --tail=20
kubectl logs -l app=chatbot-backend --tail=20
kubectl logs -l app=postgresql --tail=20

# Get Minikube IP
minikube ip

# Access applications
minikube service todo-frontend
minikube service chatbot-frontend
```

---

## Success Criteria

**Deployment is successful when:**
✅ All 7 pods are Running
✅ All health checks pass
✅ Applications accessible via browser
✅ Can create/read/update/delete tasks
✅ Chatbot can create and manage tasks
✅ Data persists after pod restarts
✅ No pods exceeding resource limits
✅ No critical errors in logs
✅ All functional tests pass

**If any item fails, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for solutions.**
