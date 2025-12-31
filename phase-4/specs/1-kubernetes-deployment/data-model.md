# Data Model: Kubernetes Resources

**Feature**: Kubernetes Deployment for Todo Chatbot
**Date**: 2025-12-30

This document defines the Kubernetes resource entities and their relationships for the Todo Chatbot deployment.

---

## Resource Hierarchy

```
Helm Chart (todo-app)
  │
  ├─ ConfigMap (app-config)
  ├─ Secret (app-secrets)
  ├─ PersistentVolumeClaim (postgres-pvc)
  │
  ├─ Deployment (postgresql)
  │   └─ Pod (postgres-xxxxx)
  │       └─ Container (postgres:15-alpine)
  │
  ├─ Service (postgresql) → ClusterIP
  │
  ├─ Deployment (todo-backend)
  │   └─ Pod (todo-backend-xxxxx)
  │       └─ Container (todo-backend:v1)
  │
  ├─ Service (todo-backend) → ClusterIP
  │
  ├─ Deployment (todo-frontend)
  │   ├─ Pod (todo-frontend-xxxxx-1)
  │   │   └─ Container (todo-frontend:v1)
  │   └─ Pod (todo-frontend-xxxxx-2)
  │       └─ Container (todo-frontend:v1)
  │
  ├─ Service (todo-frontend) → NodePort 30000
  │
  ├─ Deployment (chatbot-backend)
  │   └─ Pod (chatbot-backend-xxxxx)
  │       └─ Container (chatbot-backend:v1)
  │
  ├─ Service (chatbot-backend) → ClusterIP
  │
  ├─ Deployment (chatbot-frontend)
  │   ├─ Pod (chatbot-frontend-xxxxx-1)
  │   │   └─ Container (chatbot-frontend:v1)
  │   └─ Pod (chatbot-frontend-xxxxx-2)
  │       └─ Container (chatbot-frontend:v1)
  │
  └─ Service (chatbot-frontend) → NodePort 30001
```

---

## Entity Definitions

### 1. Docker Image

**Purpose**: Containerized application component

**Attributes**:
- `name`: Image name (e.g., `todo-backend`)
- `tag`: Version tag (e.g., `v1`)
- `base_image`: Parent image (e.g., `python:3.11-slim`)
- `size`: Image size in MB
- `layers`: Number of image layers
- `created_at`: Build timestamp

**Examples**:
| Image | Tag | Base | Size | Purpose |
|-------|-----|------|------|---------|
| todo-backend | v1 | python:3.11-slim | ~180MB | FastAPI backend |
| todo-frontend | v1 | node:18-alpine | ~250MB | Next.js frontend |
| chatbot-backend | v1 | python:3.11-slim | ~200MB | FastAPI chatbot |
| chatbot-frontend | v1 | node:18-alpine | ~270MB | Next.js chatbot UI |
| postgres | 15-alpine | alpine:3.18 | ~230MB | PostgreSQL database |

---

### 2. Helm Chart

**Purpose**: Kubernetes deployment package

**Attributes**:
- `name`: Chart name (`todo-app`)
- `version`: Chart version (SemVer, e.g., `1.0.0`)
- `app_version`: Application version (e.g., `1.0.0`)
- `description`: Chart description
- `templates`: List of Kubernetes resource templates

**Chart Metadata** (`Chart.yaml`):
```yaml
apiVersion: v2
name: todo-app
description: Todo Application with AI Chatbot
type: application
version: 1.0.0
appVersion: "1.0.0"
```

---

### 3. Deployment

**Purpose**: Manages a set of replicated pods

**Attributes**:
- `name`: Deployment name
- `replicas`: Number of pod replicas
- `selector`: Label selector for pods
- `pod_template`: Pod specification
  - `containers`: List of containers
  - `volumes`: List of volumes
  - `restart_policy`: Restart behavior
- `strategy`: Update strategy (RollingUpdate, Recreate)

**Examples**:
| Deployment | Replicas | Container | Image | CPU Limit | Memory Limit |
|------------|----------|-----------|-------|-----------|--------------|
| todo-frontend | 2 | todo-frontend | todo-frontend:v1 | 500m | 512Mi |
| todo-backend | 1 | todo-backend | todo-backend:v1 | 500m | 512Mi |
| chatbot-frontend | 2 | chatbot-frontend | chatbot-frontend:v1 | 500m | 512Mi |
| chatbot-backend | 1 | chatbot-backend | chatbot-backend:v1 | 500m | 512Mi |
| postgresql | 1 | postgres | postgres:15-alpine | 500m | 1024Mi |

---

### 4. Service

**Purpose**: Exposes a set of pods as a network service

**Attributes**:
- `name`: Service name
- `type`: Service type (ClusterIP, NodePort, LoadBalancer)
- `selector`: Label selector for pods
- `ports`: List of port mappings
  - `port`: Service port
  - `targetPort`: Container port
  - `nodePort`: External port (NodePort only)
  - `protocol`: TCP/UDP

**Examples**:
| Service | Type | Port | TargetPort | NodePort | Access |
|---------|------|------|------------|----------|--------|
| todo-frontend | NodePort | 3000 | 3000 | 30000 | External |
| todo-backend | ClusterIP | 8000 | 8000 | - | Internal |
| chatbot-frontend | NodePort | 3001 | 3001 | 30001 | External |
| chatbot-backend | ClusterIP | 8001 | 8001 | - | Internal |
| postgresql | ClusterIP | 5432 | 5432 | - | Internal |

---

### 5. ConfigMap

**Purpose**: Stores non-sensitive configuration data

**Attributes**:
- `name`: ConfigMap name
- `data`: Key-value pairs (plaintext)

**Example Data**:
```yaml
name: app-config
data:
  DATABASE_HOST: "postgresql"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "todoapp"
  TODO_API_URL: "http://todo-backend:8000"
  CHATBOT_API_URL: "http://chatbot-backend:8001"
  TODO_FRONTEND_PORT: "3000"
  CHATBOT_FRONTEND_PORT: "3001"
  ENVIRONMENT: "development"
```

---

### 6. Secret

**Purpose**: Stores sensitive configuration data

**Attributes**:
- `name`: Secret name
- `type`: Secret type (Opaque, kubernetes.io/tls, etc.)
- `data`: Key-value pairs (base64-encoded)

**Example Data**:
```yaml
name: app-secrets
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded>
  SECRET_KEY: <base64-encoded>
  OPENAI_API_KEY: <base64-encoded>
  DATABASE_URL: <base64-encoded>
```

**Security Requirements**:
- Never commit to Git
- Values templated from Helm values: `{{ .Values.secrets.* | b64enc }}`
- Mounted as environment variables or files in pods

---

### 7. PersistentVolumeClaim (PVC)

**Purpose**: Requests persistent storage

**Attributes**:
- `name`: PVC name
- `access_modes`: How volume is mounted (ReadWriteOnce, ReadWriteMany)
- `storage`: Requested storage size
- `storage_class`: Storage provisioner (standard, fast, etc.)
- `volume_name`: Bound PersistentVolume name

**Example**:
```yaml
name: postgres-pvc
accessModes:
  - ReadWriteOnce
storage: 5Gi
storageClassName: standard
```

**Usage**:
- Mounted to PostgreSQL pod at `/var/lib/postgresql/data`
- Survives pod restarts and deletions
- Data persists across deployments

---

### 8. Container

**Purpose**: Running instance of a Docker image

**Attributes**:
- `name`: Container name
- `image`: Docker image reference
- `imagePullPolicy`: When to pull image (Always, IfNotPresent, Never)
- `ports`: Exposed ports
- `env`: Environment variables
  - `name`: Variable name
  - `value`: Direct value (or)
  - `valueFrom`: Reference to ConfigMap/Secret
- `resources`: Resource requests and limits
  - `requests`: Minimum resources (CPU, memory)
  - `limits`: Maximum resources (CPU, memory)
- `probes`: Health checks
  - `livenessProbe`: Is container alive?
  - `readinessProbe`: Is container ready for traffic?

**Resource Specifications**:
| Container | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| todo-frontend | 200m | 500m | 256Mi | 512Mi |
| todo-backend | 250m | 500m | 256Mi | 512Mi |
| chatbot-frontend | 200m | 500m | 256Mi | 512Mi |
| chatbot-backend | 250m | 500m | 256Mi | 512Mi |
| postgres | 250m | 500m | 512Mi | 1024Mi |

---

## Relationships

### 1. Service → Deployment (Pod Selector)

```yaml
Service:
  selector:
    app: todo-backend
    version: v1

Deployment:
  template:
    metadata:
      labels:
        app: todo-backend
        version: v1
```

**Relationship**: Service routes traffic to pods matching labels

---

### 2. Deployment → ConfigMap (Environment Variables)

```yaml
Deployment:
  spec:
    containers:
      - name: todo-backend
        envFrom:
          - configMapRef:
              name: app-config  # All keys become env vars
```

**Relationship**: Deployment injects ConfigMap data as environment variables

---

### 3. Deployment → Secret (Environment Variables)

```yaml
Deployment:
  spec:
    containers:
      - name: todo-backend
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: DATABASE_URL
```

**Relationship**: Deployment injects Secret data as environment variables

---

### 4. Deployment → PVC (Volume Mount)

```yaml
Deployment (postgres):
  spec:
    volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
    containers:
      - name: postgres
        volumeMounts:
          - name: postgres-storage
            mountPath: /var/lib/postgresql/data
```

**Relationship**: Deployment mounts PVC as volume in container

---

### 5. Helm Chart → All Resources (Ownership)

```yaml
All Resources:
  metadata:
    labels:
      app.kubernetes.io/name: {{ .Chart.Name }}
      app.kubernetes.io/instance: {{ .Release.Name }}
      app.kubernetes.io/version: {{ .Chart.AppVersion }}
      app.kubernetes.io/managed-by: {{ .Release.Service }}
```

**Relationship**: Helm manages lifecycle of all resources (install, upgrade, rollback, delete)

---

## State Transitions

### Pod Lifecycle

```
Pending → ContainerCreating → Running → Succeeded/Failed

Conditions:
- ImagePullBackOff: Can't pull image
- CrashLoopBackOff: Container keeps crashing
- Evicted: Node out of resources
- Terminating: Pod being deleted
```

### Deployment Rollout

```
Initial → Progressing → Available → Complete

OR

Initial → Progressing → Failed (rollback)

Update Strategy: RollingUpdate
- maxUnavailable: 25%
- maxSurge: 25%
```

---

## Validation Rules

### Resource Naming

- **Pattern**: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$`
- **Max Length**: 63 characters
- **Examples**: `todo-backend`, `chatbot-frontend`, `postgres-pvc`

### Label Requirements

All resources must have:
- `app`: Component name (e.g., `todo-backend`)
- `version`: Version (e.g., `v1`)
- `app.kubernetes.io/name`: Chart name
- `app.kubernetes.io/instance`: Release name

### Resource Limits

- CPU limits must be >= requests
- Memory limits must be >= requests
- Total limits must fit within Minikube capacity (4 CPU, 8GB RAM)

---

## Next Steps

1. Create Helm chart templates following this data model
2. Ensure all relationships are correctly configured
3. Validate resource limits against Minikube capacity
4. Test deployment with `helm install --dry-run`
