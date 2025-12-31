# Quickstart: Deploy Todo Chatbot to Kubernetes

**Objective**: Get the Todo Chatbot running on Minikube in under 30 minutes

---

## Prerequisites (5 minutes)

Ensure you have these tools installed:
- Docker Desktop 4.53+ (with Gordon enabled optional)
- Minikube 1.32+
- kubectl 1.28+
- Helm 3.13+
- kubectl-ai (optional, requires OpenAI API key)

**Verification**:
```bash
docker --version     # Should be 24.0+
minikube version     # Should be v1.32+
kubectl version --client  # Should be v1.28+
helm version         # Should be v3.13+
```

---

## Step 1: Start Minikube (2 minutes)

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable addons
minikube addons enable metrics-server

# Verify cluster is running
minikube status
```

**Expected Output**:
```
minikube: Running
cluster: Running
kubectl: Correctly Configured
```

---

## Step 2: Build Docker Images (5 minutes)

```bash
# Point Docker to Minikube's daemon (images will be built in Minikube)
eval $(minikube docker-env)

# Navigate to project root
cd D:\web-todo

# Build all images
docker build -t todo-backend:v1 todo-application/backend/
docker build -t todo-frontend:v1 todo-application/frontend/
docker build -t chatbot-backend:v1 chatbot/backend/
docker build -t chatbot-frontend:v1 chatbot/frontend/

# Verify images
docker images | grep -E "todo|chatbot"
```

**Expected Output**: 4 images listed with tag `v1`

---

## Step 3: Deploy with Helm (3 minutes)

```bash
# Navigate to helm charts
cd k8s/helm-charts

# Lint chart (catches errors before deployment)
helm lint todo-app

# Dry-run install (validates against Kubernetes API)
helm install todo-app ./todo-app --dry-run --debug

# Install chart
helm install todo-app ./todo-app

# Watch pods start up
kubectl get pods --watch
```

**Expected Output**: All pods reach `Running` status within 2 minutes

---

## Step 4: Verify Deployment (2 minutes)

```bash
# Check all resources
kubectl get all

# Check pod status
kubectl get pods

# Check services
kubectl get services
```

**Expected Output**:
```
NAME                                 READY   STATUS    RESTARTS   AGE
pod/todo-frontend-xxxxx-1            1/1     Running   0          1m
pod/todo-frontend-xxxxx-2            1/1     Running   0          1m
pod/todo-backend-xxxxx               1/1     Running   0          1m
pod/chatbot-frontend-xxxxx-1         1/1     Running   0          1m
pod/chatbot-frontend-xxxxx-2         1/1     Running   0          1m
pod/chatbot-backend-xxxxx            1/1     Running   0          1m
pod/postgresql-xxxxx                 1/1     Running   0          1m

NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
service/todo-frontend      NodePort    10.96.xxx.xxx   <none>        3000:30000/TCP   1m
service/todo-backend       ClusterIP   10.96.xxx.xxx   <none>        8000/TCP         1m
service/chatbot-frontend   NodePort    10.96.xxx.xxx   <none>        3001:30001/TCP   1m
service/chatbot-backend    ClusterIP   10.96.xxx.xxx   <none>        8001/TCP         1m
service/postgresql         ClusterIP   10.96.xxx.xxx   <none>        5432/TCP         1m
```

---

## Step 5: Access Applications (1 minute)

**Method 1: Using minikube service (Easiest)**
```bash
# Open Todo Frontend
minikube service todo-frontend
# Browser opens automatically at http://<minikube-ip>:30000

# Open Chatbot Frontend (in new terminal)
minikube service chatbot-frontend
# Browser opens automatically at http://<minikube-ip>:30001
```

**Method 2: Manual URLs**
```bash
# Get Minikube IP
minikube ip
# Example output: 192.168.49.2

# Access in browser:
# Todo App: http://192.168.49.2:30000
# Chatbot: http://192.168.49.2:30001
```

---

## Step 6: Test Functionality (3 minutes)

### Todo Application
1. Open `http://<minikube-ip>:30000`
2. Create a new task
3. Mark task as complete
4. Delete task
5. Verify changes persist

### Chatbot
1. Open `http://<minikube-ip>:30001`
2. Ask: "Add a task called Meeting"
3. Ask: "Show my tasks"
4. Ask: "Delete the Meeting task"
5. Verify task appears in Todo app

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe failing pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# AI-assisted debugging
kubectl-ai "why is my pod not starting?"
```

### Image Pull Errors

```bash
# Verify you ran eval $(minikube docker-env)
# Rebuild images:
eval $(minikube docker-env)
docker build -t todo-backend:v1 todo-application/backend/
```

### Service Not Accessible

```bash
# Check service exists
kubectl get services

# Use minikube service helper
minikube service todo-frontend --url

# Or port-forward
kubectl port-forward service/todo-frontend 3000:3000
```

### Database Connection Issues

```bash
# Check PostgreSQL pod
kubectl get pods | grep postgres

# Check environment variables
kubectl exec -it <backend-pod> -- env | grep DATABASE

# Test database connection
kubectl exec -it <postgres-pod> -- psql -U postgres -c "\l"
```

---

## Cleanup

```bash
# Uninstall Helm release
helm uninstall todo-app

# Stop Minikube (preserves data)
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete
```

---

## Next Steps

1. **Scale Deployment**: `kubectl scale deployment todo-backend --replicas=3`
2. **Update Application**: Modify code, rebuild image, `helm upgrade todo-app ./todo-app`
3. **Monitor Resources**: `kubectl top pods`
4. **View Logs**: `kubectl logs -f <pod-name>`
5. **Use kubectl-ai**: `kubectl-ai "scale the todo-backend to 3 replicas"`

---

## Common kubectl-ai Commands

```bash
# Check status
kubectl-ai "show me all pods and their status"

# Debug issues
kubectl-ai "why is my pod crashing?"

# Scale services
kubectl-ai "scale the todo-backend to 3 replicas"

# Get logs
kubectl-ai "show me logs for the chatbot-backend"

# Check resources
kubectl-ai "which pods are using most CPU?"
```

---

**Total Time**: ~20 minutes (with everything pre-installed)
**Status**: Ready for development and testing!
