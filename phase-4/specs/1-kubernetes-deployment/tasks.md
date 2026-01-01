# Tasks: Kubernetes Deployment for Todo Chatbot

**Input**: Design documents from `/specs/1-kubernetes-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Infrastructure validation tests included (helm lint, dry-run, deployment checks)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1-US6)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and prerequisite verification

- [x] T001 Verify all prerequisites installed (Docker 4.53+, Minikube 1.32+, kubectl 1.28+, Helm 3.13+)
- [x] T002 Create Kubernetes manifests directory structure at `k8s/helm-charts/todo-app/`
- [x] T003 Create Helm chart subdirectories: `k8s/helm-charts/todo-app/templates/` and `k8s/helm-charts/todo-app/charts/`
- [x] T004 Update root `.gitignore` to exclude `k8s/helm-charts/todo-app/values-*.yaml` (environment-specific values)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Start Minikube cluster - MUST be complete before ANY deployment tasks

**⚠️ CRITICAL**: No deployment work can begin until Minikube is running

- [x] T005 Start Minikube cluster with `minikube start --cpus=4 --memory=8192 --driver=docker`
- [x] T006 Enable Minikube addons: `minikube addons enable metrics-server`
- [x] T007 Verify Minikube status with `minikube status` (should show Running)
- [x] T008 Point Docker to Minikube's daemon with `eval $(minikube docker-env)` (required for local image builds)

**Checkpoint**: Minikube cluster ready - containerization and deployment can now begin

---

## Phase 3: User Story 2 - Containerize Applications with Docker (Priority: P1) 🎯

**Goal**: Create production-ready Docker images for all 4 application components

**Independent Test**: Build all images successfully and verify they start without errors using `docker run`

### Todo Application Backend Dockerfile

- [x] T009 [P] [US2] Create `.dockerignore` in `todo-application/backend/` excluding `node_modules`, `.git`, `.env`, `__pycache__`, `*.pyc`, `.pytest_cache`, `venv/`
- [x] T010 [US2] Create `Dockerfile` in `todo-application/backend/` with multi-stage build:
  - Builder stage: FROM `python:3.11-slim`, WORKDIR `/app`, COPY `requirements.txt`, RUN `pip install --no-cache-dir --user`
  - Runtime stage: FROM `python:3.11-slim`, COPY from builder, create non-root user `python`, USER `python`, EXPOSE `8000`, CMD `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [x] T011 [US2] Build and test Todo backend image: `docker build -t todo-backend:v1 todo-application/backend/` and verify starts with `docker run --rm -p 8000:8000 todo-backend:v1`
- [x] T012 [US2] Verify Todo backend image size is under 500MB with `docker images todo-backend:v1`

### Todo Application Frontend Dockerfile

- [x] T013 [P] [US2] Create `.dockerignore` in `todo-application/frontend/` excluding `node_modules`, `.next`, `.git`, `.env*`, `*.log`, `.DS_Store`
- [x] T014 [US2] Create `Dockerfile` in `todo-application/frontend/` with multi-stage build:
  - Builder stage: FROM `node:18-alpine`, WORKDIR `/app`, COPY `package*.json`, RUN `npm ci`, COPY `src/ tsconfig.json next.config.js`, RUN `npm run build`
  - Runtime stage: FROM `node:18-alpine`, COPY from builder `.next/ public/ package.json`, RUN `npm install --production --ignore-scripts`, create non-root user `node`, USER `node`, EXPOSE `3000`, CMD `npm start`
- [x] T015 [US2] Build and test Todo frontend image: `docker build -t todo-frontend:v1 todo-application/frontend/` and verify starts with `docker run --rm -p 3000:3000 todo-frontend:v1`
- [x] T016 [US2] Verify Todo frontend image size is under 500MB with `docker images todo-frontend:v1`

### Chatbot Backend Dockerfile

- [x] T017 [P] [US2] Create `.dockerignore` in `chatbot/backend/` excluding `node_modules`, `.git`, `.env`, `__pycache__`, `*.pyc`, `.pytest_cache`, `venv/`
- [x] T018 [US2] Create `Dockerfile` in `chatbot/backend/` with multi-stage build:
  - Builder stage: FROM `python:3.11-slim`, WORKDIR `/app`, COPY `requirements.txt`, RUN `pip install --no-cache-dir --user`
  - Runtime stage: FROM `python:3.11-slim`, COPY from builder, COPY `src/`, create non-root user `python`, USER `python`, EXPOSE `8001`, CMD `uvicorn src.api.main:app --host 0.0.0.0 --port 8001`
- [x] T019 [US2] Build and test Chatbot backend image: `docker build -t chatbot-backend:v1 chatbot/backend/` and verify starts with `docker run --rm -p 8001:8001 chatbot-backend:v1`
- [x] T020 [US2] Verify Chatbot backend image size is under 500MB with `docker images chatbot-backend:v1`

### Chatbot Frontend Dockerfile

- [x] T021 [P] [US2] Create `.dockerignore` in `chatbot/frontend/` excluding `node_modules`, `.next`, `.git`, `.env*`, `*.log`, `.DS_Store`
- [x] T022 [US2] Create `Dockerfile` in `chatbot/frontend/` with multi-stage build:
  - Builder stage: FROM `node:18-alpine`, WORKDIR `/app`, COPY `package*.json`, RUN `npm ci`, COPY `src/ tsconfig.json next.config.js`, RUN `npm run build`
  - Runtime stage: FROM `node:18-alpine`, COPY from builder `.next/ public/ package.json`, RUN `npm install --production --ignore-scripts`, create non-root user `node`, USER `node`, EXPOSE `3001`, CMD `npm start`
- [x] T023 [US2] Build and test Chatbot frontend image: `docker build -t chatbot-frontend:v1 chatbot/frontend/` and verify starts with `docker run --rm -p 3001:3001 chatbot-frontend:v1`
- [x] T024 [US2] Verify Chatbot frontend image size is under 500MB with `docker images chatbot-frontend:v1`

### Image Verification

- [x] T025 [US2] Verify all 4 images are available in Minikube with `docker images | grep -E "todo|chatbot"`
- [ ] T026 [US2] Run Docker security scan on all images: `docker scan todo-backend:v1 todo-frontend:v1 chatbot-backend:v1 chatbot-frontend:v1` (check for critical vulnerabilities)

**Checkpoint**: All Docker images built successfully, running as non-root, under 500MB, no critical vulnerabilities

---

## Phase 4: User Story 3 - Create Helm Charts for Deployment (Priority: P1) 🎯

**Goal**: Create complete Helm chart with all Kubernetes resource templates

**Independent Test**: Run `helm lint` and `helm install --dry-run --debug` successfully

### Helm Chart Metadata

- [x] T027 [P] [US3] Create `Chart.yaml` in `k8s/helm-charts/todo-app/` with `apiVersion: v2`, `name: todo-app`, `description: Todo Application with AI Chatbot`, `type: application`, `version: 1.0.0`, `appVersion: "1.0.0"`
- [x] T028 [P] [US3] Create `.helmignore` in `k8s/helm-charts/todo-app/` to exclude `.git/`, `*.md` (except Chart README), `values-*.yaml`
- [x] T029 [P] [US3] Create `README.md` in `k8s/helm-charts/todo-app/` documenting chart installation, values, and usage

### Helm Values Configuration

- [x] T030 [US3] Create `values.yaml` in `k8s/helm-charts/todo-app/` with sections:
  - `global.environment: development`
  - `images:` (todoFrontend, todoBackend, chatbotFrontend, chatbotBackend, postgres - all with `repository`, `tag`, `pullPolicy: Never`)
  - `replicas:` (todoFrontend: 2, todoBackend: 1, chatbotFrontend: 2, chatbotBackend: 1, postgres: 1)
  - `services:` (type, port, nodePort for frontends)
  - `resources:` (requests and limits for all services)
  - `config:` (databaseHost, databasePort, databaseName, apiUrls)
  - `secrets:` (postgresPassword, secretKey, openaiApiKey with placeholders)
  - `storage.postgres:` (size: 5Gi, storageClass: standard)

### Template Helpers

- [x] T031 [P] [US3] Create `templates/_helpers.tpl` in `k8s/helm-charts/todo-app/templates/` with helper templates:
  - `todo-app.name`: Chart name
  - `todo-app.fullname`: Full qualified app name
  - `todo-app.chart`: Chart name and version
  - `todo-app.labels`: Common labels
  - `todo-app.selectorLabels`: Selector labels

### Configuration Resources

- [x] T032 [P] [US3] Create `templates/configmap.yaml` with:
  - `metadata.name: app-config`
  - `data:` DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, TODO_API_URL, CHATBOT_API_URL, ENVIRONMENT
  - All values templated from `{{ .Values.config.* }}`

- [x] T033 [P] [US3] Create `templates/secrets.yaml` with:
  - `metadata.name: app-secrets`
  - `type: Opaque`
  - `data:` POSTGRES_PASSWORD, SECRET_KEY, OPENAI_API_KEY (base64-encoded via `{{ .Values.secrets.* | b64enc }}`)

### PostgreSQL Resources

- [x] T034 [P] [US3] Create `templates/postgresql-pvc.yaml` with:
  - `apiVersion: v1`, `kind: PersistentVolumeClaim`
  - `metadata.name: postgres-pvc`
  - `spec.accessModes: [ReadWriteOnce]`
  - `spec.resources.requests.storage: {{ .Values.storage.postgres.size }}`
  - `spec.storageClassName: {{ .Values.storage.postgres.storageClass }}`

- [x] T035 [US3] Create `templates/postgresql-deployment.yaml` with:
  - `apiVersion: apps/v1`, `kind: Deployment`
  - `metadata.name: postgresql`, `spec.replicas: {{ .Values.replicas.postgres }}`
  - `spec.template.spec.containers`: image `postgres:15-alpine`, ports `5432`, env from secrets, volumeMounts for PVC
  - `spec.template.spec.volumes`: persistentVolumeClaim postgres-pvc
  - Resource limits: `{{ .Values.resources.postgres.limits/requests }}`
  - Liveness/readiness probes: exec `pg_isready -U postgres`

- [x] T036 [P] [US3] Create `templates/postgresql-service.yaml` with:
  - `apiVersion: v1`, `kind: Service`
  - `metadata.name: postgresql`
  - `spec.type: ClusterIP`, `spec.ports`: port `5432`
  - `spec.selector`: app `postgresql`

### Todo Backend Resources

- [x] T037 [P] [US3] Create `templates/todo-backend-deployment.yaml` with:
  - `apiVersion: apps/v1`, `kind: Deployment`
  - `metadata.name: todo-backend`, `spec.replicas: {{ .Values.replicas.todoBackend }}`
  - `spec.template.spec.containers`: image `todo-backend:v1`, imagePullPolicy `Never`, ports `8000`
  - `env`: DATABASE_URL from secret, envFrom configMapRef `app-config`
  - Resource limits from values, readinessProbe/livenessProbe: httpGet `/health` port `8000`

- [x] T038 [P] [US3] Create `templates/todo-backend-service.yaml` with:
  - `apiVersion: v1`, `kind: Service`
  - `metadata.name: todo-backend`
  - `spec.type: ClusterIP`, `spec.ports`: port `8000`, targetPort `8000`
  - `spec.selector`: app `todo-backend`

### Todo Frontend Resources

- [x] T039 [P] [US3] Create `templates/todo-frontend-deployment.yaml` with:
  - `apiVersion: apps/v1`, `kind: Deployment`
  - `metadata.name: todo-frontend`, `spec.replicas: {{ .Values.replicas.todoFrontend }}`
  - `spec.template.spec.containers`: image `todo-frontend:v1`, imagePullPolicy `Never`, ports `3000`
  - `env`: NEXT_PUBLIC_API_URL from config
  - Resource limits from values, readinessProbe/livenessProbe: httpGet `/` port `3000`

- [x] T040 [P] [US3] Create `templates/todo-frontend-service.yaml` with:
  - `apiVersion: v1`, `kind: Service`
  - `metadata.name: todo-frontend`
  - `spec.type: NodePort`, `spec.ports`: port `3000`, targetPort `3000`, nodePort `30000`
  - `spec.selector`: app `todo-frontend`

### Chatbot Backend Resources

- [x] T041 [P] [US3] Create `templates/chatbot-backend-deployment.yaml` with:
  - `apiVersion: apps/v1`, `kind: Deployment`
  - `metadata.name: chatbot-backend`, `spec.replicas: {{ .Values.replicas.chatbotBackend }}`
  - `spec.template.spec.containers`: image `chatbot-backend:v1`, imagePullPolicy `Never`, ports `8001`
  - `env`: DATABASE_URL, OPENAI_API_KEY from secret, TODO_API_URL from config
  - Resource limits from values, readinessProbe/livenessProbe: httpGet `/health` port `8001`

- [x] T042 [P] [US3] Create `templates/chatbot-backend-service.yaml` with:
  - `apiVersion: v1`, `kind: Service`
  - `metadata.name: chatbot-backend`
  - `spec.type: ClusterIP`, `spec.ports`: port `8001`, targetPort `8001`
  - `spec.selector`: app `chatbot-backend`

### Chatbot Frontend Resources

- [x] T043 [P] [US3] Create `templates/chatbot-frontend-deployment.yaml` with:
  - `apiVersion: apps/v1`, `kind: Deployment`
  - `metadata.name: chatbot-frontend`, `spec.replicas: {{ .Values.replicas.chatbotFrontend }}`
  - `spec.template.spec.containers`: image `chatbot-frontend:v1`, imagePullPolicy `Never`, ports `3001`
  - `env`: NEXT_PUBLIC_API_URL from config (chatbot-backend URL)
  - Resource limits from values, readinessProbe/livenessProbe: httpGet `/` port `3001`

- [x] T044 [P] [US3] Create `templates/chatbot-frontend-service.yaml` with:
  - `apiVersion: v1`, `kind: Service`
  - `metadata.name: chatbot-frontend`
  - `spec.type: NodePort`, `spec.ports`: port `3001`, targetPort `3001`, nodePort `30001`
  - `spec.selector`: app `chatbot-frontend`

### Helm Chart Validation

- [x] T045 [US3] Run `helm lint k8s/helm-charts/todo-app` and verify zero errors and warnings
- [x] T046 [US3] Run `helm install --dry-run --debug todo-app k8s/helm-charts/todo-app` and verify all templates render correctly
- [x] T047 [US3] Verify all resource templates have consistent labels using `{{ include "todo-app.labels" . }}`
- [x] T048 [US3] Verify all secrets values are base64-encoded using `| b64enc` template function

**Checkpoint**: Helm chart passes all validation, ready for deployment

---

## Phase 5: User Story 1 - Deploy Application to Local Kubernetes (Priority: P1) 🎯

**Goal**: Deploy entire application to Minikube using Helm

**Independent Test**: All 7 pods (2 frontends x2 replicas, 2 backends, 1 database) reach Running status within 2 minutes

### Helm Deployment

- [x] T049 [US1] Update `values.yaml` secrets section with actual values from `chatbot/backend/.env` (OPENAI_API_KEY) and generate secure SECRET_KEY and POSTGRES_PASSWORD
- [x] T050 [US1] Install Helm chart with `helm install todo-app k8s/helm-charts/todo-app`
- [x] T051 [US1] Watch pod startup with `kubectl get pods --watch` until all pods show Running status (timeout 2 minutes)
- [x] T052 [US1] Verify Helm release status with `helm list` (should show STATUS: deployed)

### Deployment Verification

- [x] T053 [P] [US1] Verify all deployments are ready with `kubectl get deployments` (READY column should match DESIRED)
- [x] T054 [P] [US1] Verify all services have endpoints with `kubectl get endpoints` (all services should have IP addresses listed)
- [x] T055 [P] [US1] Verify all pods are Running with `kubectl get pods` (STATUS column should show Running for all 7 pods)
- [x] T056 [US1] Check for any pod errors with `kubectl get pods | grep -v Running` (should be empty)
- [x] T057 [US1] Verify readiness probes passing with `kubectl get pods` (READY column should show 1/1 or 2/2 for frontends)

### Pod Logs Verification

- [x] T058 [P] [US1] Check PostgreSQL pod logs: `kubectl logs -l app=postgresql --tail=20` (should show "database system is ready to accept connections")
- [x] T059 [P] [US1] Check Todo backend logs: `kubectl logs -l app=todo-backend --tail=20` (should show "Application startup complete" or "Uvicorn running")
- [x] T060 [P] [US1] Check Todo frontend logs: `kubectl logs -l app=todo-frontend --tail=20` (should show "Ready" or "started server")
- [x] T061 [P] [US1] Check Chatbot backend logs: `kubectl logs -l app=chatbot-backend --tail=20` (should show successful startup)
- [x] T062 [P] [US1] Check Chatbot frontend logs: `kubectl logs -l app=chatbot-frontend --tail=20` (should show successful startup)

### Service Access

- [x] T063 [US1] Get Minikube IP with `minikube ip` and note for browser access
- [x] T064 [US1] Verify Todo frontend accessible: Open `http://<minikube-ip>:30000` in browser (should load homepage)
- [x] T065 [US1] Verify Chatbot frontend accessible: Open `http://<minikube-ip>:30001` in browser (should load chat interface)
- [x] T066 [US1] Alternative: Use `minikube service todo-frontend` to open browser automatically
- [x] T067 [US1] Alternative: Use `minikube service chatbot-frontend` to open browser automatically

**Checkpoint**: All services deployed and accessible via browser

---

## Phase 6: User Story 4 - Verify Application Functionality Post-Deployment (Priority: P2)

**Goal**: Confirm deployed application works end-to-end

**Independent Test**: Create/delete tasks via UI and chatbot, verify data persists

### Todo Application Testing

- [x] T068 [P] [US4] Test Todo frontend: Create a new task "Deployment Test" via UI at `http://<minikube-ip>:30000`
- [x] T069 [US4] Verify task appears in task list and persists in database
- [x] T070 [P] [US4] Test mark as complete: Click checkbox on "Deployment Test" task, verify status updates
- [x] T071 [P] [US4] Test delete: Delete "Deployment Test" task, verify it's removed from list

### Chatbot Functionality Testing

- [x] T072 [P] [US4] Test Chatbot: Open `http://<minikube-ip>:30001` and ask "Add a task called Meeting"
- [x] T073 [US4] Verify chatbot creates task and it appears in Todo app at `http://<minikube-ip>:30000`
- [x] T074 [P] [US4] Test list tasks: Ask chatbot "Show my tasks", verify it lists all current tasks
- [x] T075 [P] [US4] Test delete via chatbot: Ask "Delete the Meeting task", verify task removed

### Database Persistence Testing

- [x] T076 [US4] Test data persistence: Create a task via Todo UI, then delete todo-backend pod with `kubectl delete pod -l app=todo-backend`
- [x] T077 [US4] Wait for pod to restart (Kubernetes auto-restarts), verify task still exists (data persisted in PostgreSQL PVC)
- [x] T078 [US4] Test database connectivity: Exec into PostgreSQL pod with `kubectl exec -it $(kubectl get pod -l app=postgresql -o name) -- psql -U postgres -c "\l"` and verify `todoapp` database exists

### Health Endpoint Verification

- [x] T079 [P] [US4] Test Todo backend health: `kubectl exec -it $(kubectl get pod -l app=todo-frontend -o name | head -1) -- wget -qO- http://todo-backend:8000/health` (should return healthy status)
- [x] T080 [P] [US4] Test Chatbot backend health: `kubectl exec -it $(kubectl get pod -l app=chatbot-frontend -o name | head -1) -- wget -qO- http://chatbot-backend:8001/health` (should return healthy status)

### Resource Monitoring

- [x] T081 [US4] Check resource usage with `kubectl top pods` (verify no pod exceeding resource limits)
- [x] T082 [US4] Check node resource usage with `kubectl top nodes` (verify Minikube has available resources)

**Checkpoint**: Application fully functional, data persists, all health checks passing

---

## Phase 7: User Story 6 - Manage Deployment Lifecycle (Priority: P2)

**Goal**: Test Helm upgrade, rollback, and uninstall operations

**Independent Test**: Successfully upgrade configuration, rollback to previous version, and cleanly uninstall

### Helm Upgrade Testing

- [x] T083 [US6] Modify `values.yaml`: Change `replicas.todoBackend` from 1 to 2
- [x] T084 [US6] Upgrade Helm release with `helm upgrade todo-app k8s/helm-charts/todo-app`
- [x] T085 [US6] Verify upgrade: `kubectl get pods -l app=todo-backend` should show 2 pods Running
- [x] T086 [US6] Verify application still works: Access Todo frontend and verify tasks still accessible

### Helm Rollback Testing

- [x] T087 [US6] Check Helm history with `helm history todo-app` (should show at least 2 revisions)
- [x] T088 [US6] Rollback to previous revision with `helm rollback todo-app`
- [x] T089 [US6] Verify rollback: `kubectl get pods -l app=todo-backend` should show 1 pod Running (back to original replica count)
- [x] T090 [US6] Verify application still works after rollback

### Helm Status and Values

- [x] T091 [P] [US6] Get release status with `helm status todo-app` (should show deployed status, resources, and notes)
- [x] T092 [P] [US6] Get deployed values with `helm get values todo-app` (should show current configuration)
- [x] T093 [US6] Compare with default values: `helm get values todo-app --all` (shows merged values)

**Checkpoint**: Helm lifecycle operations (upgrade, rollback) work correctly

---

## Phase 8: User Story 5 - Use AI DevOps Tools for Operations (Priority: P3)

**Goal**: Demonstrate kubectl-ai usage for natural language Kubernetes operations

**Independent Test**: Successfully execute common operations using natural language commands

**NOTE**: This phase is optional and requires kubectl-ai installation and OpenAI API key configuration

### kubectl-ai Setup

- [ ] T094 [US5] Install kubectl-ai per `PHASE_IV_INSTRUCTIONS.md` lines 142-154
- [ ] T095 [US5] Configure OpenAI API key: `export OPENAI_API_KEY="<key-from-chatbot-backend-env>"`
- [ ] T096 [US5] Test kubectl-ai connection: `kubectl-ai "test connection"` (should respond with kubectl version or pod list)

### kubectl-ai Operations

- [ ] T097 [P] [US5] Check deployment status: `kubectl-ai "show me all pods and their status"` (compare output with `kubectl get pods`)
- [ ] T098 [P] [US5] Check service URLs: `kubectl-ai "how do I access the frontend services?"` (should provide Minikube IP + NodePort info)
- [ ] T099 [P] [US5] Scale deployment: `kubectl-ai "scale the todo-backend to 3 replicas"` and verify with `kubectl get pods -l app=todo-backend`
- [ ] T100 [US5] Scale back: `kubectl-ai "scale the todo-backend to 1 replica"`
- [ ] T101 [P] [US5] Check logs: `kubectl-ai "show me recent logs from the chatbot-backend"` (compare with `kubectl logs`)
- [ ] T102 [P] [US5] Troubleshoot: Delete a pod and ask `kubectl-ai "why is my pod crashing?"` (test debugging capabilities)

### Alternative: Standard kubectl Commands

- [ ] T103 [US5] Document standard kubectl alternatives in `k8s/helm-charts/todo-app/README.md` for users without kubectl-ai

**Checkpoint**: kubectl-ai successfully used for operations (or standard kubectl documented)

---

## Phase 9: Polish & Documentation

**Purpose**: Final documentation and cleanup

- [x] T104 [P] Update root `README.md` with Phase IV deployment section referencing `k8s/helm-charts/todo-app/README.md`
- [x] T105 [P] Update `PHASE_IV_INSTRUCTIONS.md` with any lessons learned or deployment gotchas discovered during implementation
- [x] T106 [P] Create `k8s/helm-charts/todo-app/TROUBLESHOOTING.md` documenting common issues (ImagePullBackOff, CrashLoopBackOff, service not accessible) and solutions
- [x] T107 Create deployment verification checklist in `k8s/helm-charts/todo-app/CHECKLIST.md` based on quality gates from constitution
- [x] T108 [P] Document cleanup process: `helm uninstall todo-app`, `minikube stop`, `minikube delete` in README
- [x] T109 Add resource utilization table to README showing actual vs allocated resources (from `kubectl top`)
- [x] T110 [P] Create quickstart script `k8s/helm-charts/deploy.sh` automating steps: start Minikube, build images, install chart, verify deployment
- [ ] T111 Run final validation: Execute all steps in `quickstart.md` on a fresh Minikube cluster to ensure reproducibility

**Checkpoint**: Documentation complete, deployment process reproducible

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - start Minikube BLOCKS all deployment work
- **User Story 2 (Containerize - Phase 3)**: Depends on Foundational (Minikube running with docker env)
- **User Story 3 (Helm Charts - Phase 4)**: Can start in parallel with US2 (different files)
- **User Story 1 (Deploy - Phase 5)**: Depends on US2 AND US3 complete (needs images and charts)
- **User Story 4 (Verify - Phase 6)**: Depends on US1 (needs deployed application)
- **User Story 6 (Lifecycle - Phase 7)**: Depends on US1 (needs deployed application)
- **User Story 5 (AI Tools - Phase 8)**: Depends on US1 (needs deployed application), OPTIONAL
- **Polish (Phase 9)**: Depends on all functional user stories complete

### User Story Independence

- **US2 (Containerize)**: Independent - creates Dockerfiles only
- **US3 (Helm Charts)**: Independent - creates YAML templates only
- **US1 (Deploy)**: Depends on US2 + US3 (needs images and charts)
- **US4 (Verify)**: Depends on US1 (tests deployed app)
- **US6 (Lifecycle)**: Depends on US1 (tests Helm operations)
- **US5 (AI Tools)**: Optional, depends on US1

### Parallel Opportunities

**Within US2 (Containerize)**:
- T009-T012 (Todo backend) can run in parallel with T013-T016 (Todo frontend)
- T017-T020 (Chatbot backend) can run in parallel with T021-T024 (Chatbot frontend)
- All 4 Dockerfiles can be created simultaneously by different developers

**Within US3 (Helm Charts)**:
- T027-T029 (metadata) in parallel with T030 (values)
- T032-T033 (ConfigMap/Secret) in parallel with T034-T036 (PostgreSQL)
- T037-T048 (all deployments and services) can run in parallel (13 tasks!)

**Across User Stories**:
- US2 (Dockerfiles) can run in parallel with US3 (Helm charts) - different file sets
- US4 (Verify) tests can run in parallel after US1 deployment complete

---

## Parallel Example: User Story 3 (Helm Templates)

```bash
# Launch all deployment/service template creation together:
Task T037: "Create todo-backend-deployment.yaml"
Task T038: "Create todo-backend-service.yaml"
Task T039: "Create todo-frontend-deployment.yaml"
Task T040: "Create todo-frontend-service.yaml"
Task T041: "Create chatbot-backend-deployment.yaml"
Task T042: "Create chatbot-backend-service.yaml"
Task T043: "Create chatbot-frontend-deployment.yaml"
Task T044: "Create chatbot-frontend-service.yaml"

# All 8 tasks can execute simultaneously (different files, no dependencies)
```

---

## Implementation Strategy

### MVP First (Complete Core Deployment)

1. Complete Phase 1: Setup (verify prerequisites)
2. Complete Phase 2: Foundational (start Minikube)
3. Complete Phase 3: User Story 2 (containerize all applications)
4. Complete Phase 4: User Story 3 (create Helm chart)
5. Complete Phase 5: User Story 1 (deploy to Minikube)
6. **STOP and VALIDATE**: Test deployment independently
7. **MVP COMPLETE**: Application running on Kubernetes!

### Incremental Enhancement

1. MVP complete (US1 + US2 + US3) → Working deployment
2. Add User Story 4 → Verify functionality → Confidence in deployment
3. Add User Story 6 → Test lifecycle → Operational readiness
4. Add User Story 5 → AI tools → Enhanced productivity
5. Add Polish → Documentation → Production-ready

### Parallel Team Strategy

With multiple developers after Foundational phase complete:

- **Developer A**: User Story 2 (Dockerfiles) - T009-T026
- **Developer B**: User Story 3 (Helm charts) - T027-T048
- **Developer C**: Documentation and scripts (Phase 9 prep)

Once US2 + US3 complete:
- **All developers together**: Deploy (US1), verify (US4), test lifecycle (US6)

---

## Task Counts

- **Total Tasks**: 111
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (US2 - Containerize)**: 18 tasks (4 Dockerfiles + verification)
- **Phase 4 (US3 - Helm Charts)**: 22 tasks (metadata + 13 templates + validation)
- **Phase 5 (US1 - Deploy)**: 19 tasks (deployment + verification + access)
- **Phase 6 (US4 - Verify)**: 15 tasks (functionality + persistence + monitoring)
- **Phase 7 (US6 - Lifecycle)**: 11 tasks (upgrade + rollback + status)
- **Phase 8 (US5 - AI Tools)**: 10 tasks (optional kubectl-ai usage)
- **Phase 9 (Polish)**: 8 tasks (documentation + scripts)

**Parallel Tasks**: 45 tasks marked [P] (40% can run in parallel)

**Independent User Stories**: US2 and US3 can run in parallel (40 tasks)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [US#] label maps task to specific user story for traceability
- Verify Minikube running (`minikube status`) before starting US2/US3
- Always run `eval $(minikube docker-env)` in each new terminal session
- Commit Dockerfiles and Helm charts to Git (NOT values-*.yaml with secrets)
- Use `helm upgrade` not `helm install` for subsequent deployments
- Stop at any checkpoint to validate story independently
- Document any deviations from plan in comments within YAML files

---

**Total Estimated Time**: 8-12 hours (with parallel execution)
**MVP Time** (US1+US2+US3): 4-6 hours
**Critical Path**: Setup → Foundational → US2 → US3 → US1 (sequential)
**Suggested MVP Scope**: Complete through Phase 5 (US1 Deploy)
