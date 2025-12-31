# Helm Chart Contract: todo-app

**Chart Name**: todo-app
**Version**: 1.0.0
**App Version**: 1.0.0

This document defines the structure and contracts for the Helm chart.

---

## Chart.yaml

```yaml
apiVersion: v2
name: todo-app
description: Todo Application with AI Chatbot - Full stack deployment to Kubernetes
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - chatbot
  - fastapi
  - nextjs
  - postgresql
maintainers:
  - name: Todo Team
```

---

## values.yaml Structure

```yaml
# Global configuration
global:
  environment: development

# Docker images
images:
  todoFrontend:
    repository: todo-frontend
    tag: v1
    pullPolicy: Never
  todoBackend:
    repository: todo-backend
    tag: v1
    pullPolicy: Never
  chatbotFrontend:
    repository: chatbot-frontend
    tag: v1
    pullPolicy: Never
  chatbotBackend:
    repository: chatbot-backend
    tag: v1
    pullPolicy: Never
  postgres:
    repository: postgres
    tag: 15-alpine
    pullPolicy: IfNotPresent

# Replica counts
replicas:
  todoFrontend: 2
  todoBackend: 1
  chatbotFrontend: 2
  chatbotBackend: 1
  postgres: 1

# Service configuration
services:
  todoFrontend:
    type: NodePort
    port: 3000
    nodePort: 30000
  todoBackend:
    type: ClusterIP
    port: 8000
  chatbotFrontend:
    type: NodePort
    port: 3001
    nodePort: 30001
  chatbotBackend:
    type: ClusterIP
    port: 8001
  postgres:
    type: ClusterIP
    port: 5432

# Resource limits
resources:
  todoFrontend:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  todoBackend:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  chatbotFrontend:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  chatbotBackend:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  postgres:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1024Mi

# Configuration (non-sensitive)
config:
  databaseHost: postgresql
  databasePort: 5432
  databaseName: todoapp
  todoApiUrl: http://todo-backend:8000
  chatbotApiUrl: http://chatbot-backend:8001

# Secrets (sensitive - override with --set or values file)
secrets:
  postgresPassword: changeme123
  secretKey: your-secret-key-here-change-in-production
  openaiApiKey: your-openai-api-key-here

# Storage
storage:
  postgres:
    size: 5Gi
    storageClass: standard
```

---

## Template Helpers (_helpers.tpl)

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## Directory Structure

```
todo-app/
├── Chart.yaml                     # Chart metadata
├── values.yaml                    # Default values
├── .helmignore                    # Files to ignore
├── README.md                      # Chart documentation
├── templates/
│   ├── _helpers.tpl              # Template helpers
│   ├── configmap.yaml            # Application configuration
│   ├── secrets.yaml              # Sensitive data
│   ├── postgresql-pvc.yaml       # Database persistent storage
│   ├── postgresql-deployment.yaml
│   ├── postgresql-service.yaml
│   ├── todo-backend-deployment.yaml
│   ├── todo-backend-service.yaml
│   ├── todo-frontend-deployment.yaml
│   ├── todo-frontend-service.yaml
│   ├── chatbot-backend-deployment.yaml
│   ├── chatbot-backend-service.yaml
│   ├── chatbot-frontend-deployment.yaml
│   └── chatbot-frontend-service.yaml
└── charts/                        # Dependencies (empty for now)
```

---

## Deployment Commands

```bash
# Lint chart
helm lint ./todo-app

# Dry-run install
helm install todo-app ./todo-app --dry-run --debug

# Install chart
helm install todo-app ./todo-app

# Upgrade chart
helm upgrade todo-app ./todo-app

# Rollback to previous revision
helm rollback todo-app

# Uninstall chart
helm uninstall todo-app

# Override values
helm install todo-app ./todo-app --set secrets.openaiApiKey=sk-your-key
```
