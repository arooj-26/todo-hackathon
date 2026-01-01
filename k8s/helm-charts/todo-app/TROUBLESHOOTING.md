# Troubleshooting Guide

Common issues and solutions for the Todo App Kubernetes deployment.

## Table of Contents

- [Image Pull Errors](#image-pull-errors)
- [Pod Crash Loops](#pod-crash-loops)
- [Service Not Accessible](#service-not-accessible)
- [Database Connection Issues](#database-connection-issues)
- [Resource Issues](#resource-issues)
- [Helm Issues](#helm-issues)
- [Minikube Issues](#minikube-issues)

---

## Image Pull Errors

### Issue: `ImagePullBackOff` or `ErrImagePull`

**Symptoms:**
```
kubectl get pods
NAME                              READY   STATUS             RESTARTS   AGE
todo-frontend-xxx                 0/1     ImagePullBackOff   0          2m
```

**Cause:** Pod cannot pull the Docker image (usually because it doesn't exist in Minikube's Docker daemon).

**Solution:**

1. **Verify Docker environment is set:**
   ```bash
   eval $(minikube docker-env)
   ```

2. **Check if images exist in Minikube:**
   ```bash
   minikube ssh "docker images | grep -E 'todo|chatbot'"
   ```

3. **Rebuild images if missing:**
   ```bash
   eval $(minikube docker-env)
   docker build -t todo-backend:v1 ../../todo-application/backend/
   docker build -t todo-frontend:v1 ../../todo-application/frontend/
   docker build -t chatbot-backend:v1 ../../chatbot/backend/
   docker build -t chatbot-frontend:v1 ../../chatbot/frontend/
   ```

4. **Verify imagePullPolicy is set to `Never`:**
   ```bash
   kubectl get deployment todo-frontend -o yaml | grep imagePullPolicy
   ```

5. **Restart the deployment:**
   ```bash
   kubectl rollout restart deployment todo-frontend
   ```

---

## Pod Crash Loops

### Issue: `CrashLoopBackOff`

**Symptoms:**
```
kubectl get pods
NAME                              READY   STATUS              RESTARTS   AGE
chatbot-backend-xxx               0/1     CrashLoopBackOff    5          3m
```

**Diagnosis:**

1. **Check pod logs:**
   ```bash
   kubectl logs <pod-name>
   kubectl logs <pod-name> --previous  # For previous crash
   ```

2. **Describe the pod:**
   ```bash
   kubectl describe pod <pod-name>
   ```

### Common Causes & Solutions:

#### A. Missing Environment Variables

**Error in logs:**
```
KeyError: 'OPENAI_API_KEY'
KeyError: 'DATABASE_URL'
```

**Solution:**
1. Check secrets are created:
   ```bash
   kubectl get secrets app-secrets -o yaml
   ```

2. Verify secrets are properly base64 encoded:
   ```bash
   kubectl get secret app-secrets -o jsonpath='{.data.OPENAI_API_KEY}' | base64 --decode
   ```

3. Update values.yaml and redeploy:
   ```bash
   kubectl delete -f ../../rendered/02-secrets.yaml
   kubectl apply -f ../../rendered/02-secrets.yaml
   kubectl rollout restart deployment chatbot-backend
   ```

#### B. Database Connection Failed

**Error in logs:**
```
psycopg2.OperationalError: could not connect to server
sqlalchemy.exc.OperationalError: connection refused
```

**Solution:**
1. Check PostgreSQL is running:
   ```bash
   kubectl get pods -l app=postgresql
   kubectl logs -l app=postgresql --tail=20
   ```

2. Verify database service exists:
   ```bash
   kubectl get svc postgresql
   kubectl get endpoints postgresql
   ```

3. Test database connectivity from a pod:
   ```bash
   kubectl exec -it $(kubectl get pod -l app=todo-backend -o name | head -1) -- \
     ping -c 3 postgresql
   ```

4. Check PostgreSQL pod logs for errors:
   ```bash
   kubectl logs -l app=postgresql --tail=50
   ```

#### C. Application Port Conflicts

**Error in logs:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
1. Check port configuration in deployment:
   ```bash
   kubectl get deployment <deployment-name> -o yaml | grep containerPort
   ```

2. Verify no port conflicts in values.yaml

3. Restart the pod:
   ```bash
   kubectl delete pod <pod-name>
   ```

---

## Service Not Accessible

### Issue: Cannot access application in browser

**Symptoms:**
- `http://<minikube-ip>:30000` times out or connection refused
- "This site can't be reached" error

**Diagnosis:**

1. **Verify Minikube is running:**
   ```bash
   minikube status
   ```

2. **Get Minikube IP:**
   ```bash
   minikube ip
   ```

3. **Check service configuration:**
   ```bash
   kubectl get svc
   ```

4. **Verify NodePort:**
   ```bash
   kubectl get svc todo-frontend -o yaml | grep nodePort
   ```

**Solutions:**

#### A. Service Not Created

```bash
# Recreate service
kubectl apply -f ../../rendered/06-todo-frontend.yaml
```

#### B. NodePort Not Accessible

```bash
# Use minikube service command instead
minikube service todo-frontend

# Or use port-forward as alternative
kubectl port-forward service/todo-frontend 3000:3000
# Then access at http://localhost:3000
```

#### C. Pod Not Ready

```bash
# Check pod status
kubectl get pods -l app=todo-frontend

# Check readiness probe
kubectl describe pod <pod-name> | grep -A5 Readiness
```

#### D. Firewall Blocking

On Windows, check Windows Firewall or antivirus is not blocking ports 30000-30001.

---

## Database Connection Issues

### Issue: Backend cannot connect to PostgreSQL

**Symptoms:**
- Backend logs show connection errors
- Health checks failing
- 500 errors when accessing API

**Solution:**

1. **Verify PostgreSQL is healthy:**
   ```bash
   kubectl exec -it $(kubectl get pod -l app=postgresql -o name) -- \
     psql -U postgres -c "\l"
   ```

2. **Check DATABASE_URL format in secrets:**
   ```bash
   # Should be: postgresql://postgres:<password>@postgresql:5432/todoapp
   kubectl get secret app-secrets -o jsonpath='{.data}' | jq
   ```

3. **Test connection from backend pod:**
   ```bash
   kubectl exec -it $(kubectl get pod -l app=todo-backend -o name | head -1) -- \
     env | grep DATABASE
   ```

4. **Check PVC is mounted:**
   ```bash
   kubectl get pvc postgres-pvc
   kubectl describe pvc postgres-pvc
   ```

5. **Recreate database if corrupted:**
   ```bash
   kubectl delete pod -l app=postgresql
   # Pod will auto-restart, data persists in PVC
   ```

---

## Resource Issues

### Issue: Pod stuck in `Pending` state

**Symptoms:**
```
kubectl get pods
NAME                              READY   STATUS    RESTARTS   AGE
todo-frontend-xxx                 0/1     Pending   0          5m
```

**Cause:** Insufficient cluster resources.

**Solution:**

1. **Check pod events:**
   ```bash
   kubectl describe pod <pod-name>
   ```

2. **Check node resources:**
   ```bash
   kubectl top nodes
   kubectl describe nodes
   ```

3. **Restart Minikube with more resources:**
   ```bash
   minikube stop
   minikube start --cpus=4 --memory=8192 --driver=docker
   ```

4. **Reduce resource requests in values.yaml:**
   ```yaml
   resources:
     todoFrontend:
       requests:
         cpu: 100m      # Reduced from 200m
         memory: 128Mi  # Reduced from 256Mi
   ```

5. **Reduce replica counts:**
   ```yaml
   replicas:
     todoFrontend: 1  # Reduced from 2
     chatbotFrontend: 1  # Reduced from 2
   ```

---

## Helm Issues

### Issue: Helm lint fails with "Chart.yaml missing"

**Symptoms:**
```
Error: Chart.yaml file is missing
```

**Cause:** Windows path escaping issue or file encoding problem.

**Solution:**

**Option 1: Use rendered manifests instead:**
```bash
kubectl apply -f ../../rendered/
```

**Option 2: Use absolute Unix-style path:**
```bash
cd /d/web-todo
helm lint ./k8s/helm-charts/todo-app
```

**Option 3: Recreate Chart.yaml:**
```bash
# Delete and recreate the file with correct encoding
rm k8s/helm-charts/todo-app/Chart.yaml
# Copy content and create new file
```

### Issue: Helm cannot connect to Kubernetes

**Symptoms:**
```
Error: kubernetes cluster unreachable
```

**Solution:**
1. Verify kubectl works:
   ```bash
   kubectl cluster-info
   ```

2. Check kubeconfig:
   ```bash
   kubectl config current-context
   ```

3. Restart Minikube:
   ```bash
   minikube stop
   minikube start
   ```

---

## Minikube Issues

### Issue: Minikube won't start

**Error:**
```
Exiting due to HOST_DEL: Failed to start host
```

**Solution:**

1. **Delete and recreate cluster:**
   ```bash
   minikube delete
   minikube start --cpus=4 --memory=8192 --driver=docker
   ```

2. **Check Docker is running:**
   ```bash
   docker version
   ```

3. **Try different driver:**
   ```bash
   minikube start --driver=virtualbox
   # or
   minikube start --driver=hyperv
   ```

### Issue: Cannot access services via NodePort

**Solution:**

1. **Use minikube tunnel (requires admin/sudo):**
   ```bash
   minikube tunnel
   ```

2. **Use minikube service:**
   ```bash
   minikube service todo-frontend --url
   ```

3. **Use port-forward:**
   ```bash
   kubectl port-forward svc/todo-frontend 3000:3000
   ```

---

## General Debugging Commands

### Check Everything

```bash
# All resources
kubectl get all

# Events (recent issues)
kubectl get events --sort-by='.lastTimestamp' | tail -20

# Resource usage
kubectl top pods
kubectl top nodes

# Detailed pod info
kubectl describe pod <pod-name>

# Logs with timestamps
kubectl logs <pod-name> --timestamps=true

# Multiple pod logs
kubectl logs -l app=todo-backend --all-containers=true
```

### Complete Reset

If all else fails:

```bash
# Delete all resources
kubectl delete -f ../../rendered/

# Or if using Helm
helm uninstall todo-app

# Reset Minikube
minikube stop
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker

# Rebuild and redeploy
eval $(minikube docker-env)
# Rebuild all images...
# Redeploy...
```

---

## Getting Help

If issues persist:

1. **Collect diagnostic information:**
   ```bash
   kubectl get all
   kubectl get events --sort-by='.lastTimestamp' | tail -30
   kubectl logs <failing-pod-name>
   kubectl describe pod <failing-pod-name>
   minikube logs
   ```

2. **Check versions:**
   ```bash
   docker version
   minikube version
   kubectl version
   helm version
   ```

3. **Review configuration:**
   ```bash
   kubectl get cm app-config -o yaml
   kubectl get secret app-secrets -o yaml
   kubectl get deploy <deployment-name> -o yaml
   ```

4. **Search for similar issues:**
   - Kubernetes documentation
   - Minikube GitHub issues
   - Stack Overflow

---

## Prevention

**Best Practices:**

1. Always set Docker environment before building:
   ```bash
   eval $(minikube docker-env)
   ```

2. Use `imagePullPolicy: Never` for local images

3. Check resources before deployment:
   ```bash
   kubectl top nodes
   ```

4. Monitor pod health after deployment:
   ```bash
   kubectl get pods --watch
   ```

5. Keep secrets out of Git:
   - Use `.gitignore` for `values-*.yaml`
   - Never commit actual API keys

6. Test incrementally:
   - Deploy PostgreSQL first
   - Then backends
   - Then frontends
   - Verify at each step
