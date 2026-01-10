#!/bin/bash
# Security audit script
# Verifies no secrets in source code, proper credential management

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

FAILED=0

print_status "Running security audit..."
echo ""

# Check 1: No secrets in source code
print_status "Check 1: Scanning for hardcoded secrets..."

# Common patterns for secrets
PATTERNS=(
    "password\s*=\s*['\"][^'\"]{8,}"
    "api[_-]?key\s*=\s*['\"][^'\"]{20,}"
    "secret\s*=\s*['\"][^'\"]{20,}"
    "token\s*=\s*['\"][^'\"]{20,}"
    "aws_access_key_id"
    "private_key"
    "BEGIN RSA PRIVATE KEY"
    "BEGIN PRIVATE KEY"
    "sk-[a-zA-Z0-9]{20,}"
)

SECRET_FOUND=0

for pattern in "${PATTERNS[@]}"; do
    MATCHES=$(grep -r -i -E "${pattern}" \
        --include="*.py" \
        --include="*.js" \
        --include="*.ts" \
        --include="*.tsx" \
        --include="*.yaml" \
        --include="*.yml" \
        --exclude-dir=node_modules \
        --exclude-dir=venv \
        --exclude-dir=.git \
        --exclude-dir=dist \
        --exclude-dir=build \
        ../../phase-5/services/ 2>/dev/null || true)

    if [ -n "${MATCHES}" ]; then
        print_error "Potential secret found: ${pattern}"
        echo "${MATCHES}" | head -5
        SECRET_FOUND=1
    fi
done

if [ ${SECRET_FOUND} -eq 0 ]; then
    print_success "No hardcoded secrets found in source code"
else
    print_error "Hardcoded secrets detected"
    FAILED=1
fi

# Check 2: Environment variables not in Dockerfiles
print_status "Check 2: Checking Dockerfiles for sensitive environment variables..."

ENV_FOUND=0

for dockerfile in $(find ../../phase-5/services -name "Dockerfile" -o -name "dockerfile"); do
    SENSITIVE_ENVS=$(grep -i "ENV.*\(PASSWORD\|SECRET\|KEY\|TOKEN\)" ${dockerfile} || true)

    if [ -n "${SENSITIVE_ENVS}" ]; then
        print_error "Sensitive ENV in ${dockerfile}"
        echo "${SENSITIVE_ENVS}"
        ENV_FOUND=1
    fi
done

if [ ${ENV_FOUND} -eq 0 ]; then
    print_success "No sensitive environment variables in Dockerfiles"
else
    print_error "Sensitive environment variables found in Dockerfiles"
    FAILED=1
fi

# Check 3: .env files not committed
print_status "Check 3: Checking for committed .env files..."

ENV_FILES=$(find ../../phase-5 -name ".env" -not -name ".env.example" 2>/dev/null || true)

if [ -n "${ENV_FILES}" ]; then
    print_error ".env files found in repository:"
    echo "${ENV_FILES}"
    FAILED=1
else
    print_success "No .env files found in repository"
fi

# Check 4: Kubernetes secrets properly configured
print_status "Check 4: Verifying Kubernetes secrets..."

NAMESPACE="${NAMESPACE:-todo-app}"

if kubectl get secret todo-app-secrets -n ${NAMESPACE} &>/dev/null; then
    # Check secret keys
    REQUIRED_KEYS=("postgresPassword" "jwtSecret" "secretKey")
    MISSING_KEYS=()

    for key in "${REQUIRED_KEYS[@]}"; do
        if ! kubectl get secret todo-app-secrets -n ${NAMESPACE} -o jsonpath="{.data.${key}}" &>/dev/null; then
            MISSING_KEYS+=("${key}")
        fi
    done

    if [ ${#MISSING_KEYS[@]} -eq 0 ]; then
        print_success "All required secret keys present"
    else
        print_error "Missing secret keys: ${MISSING_KEYS[*]}"
        FAILED=1
    fi
else
    print_warning "Kubernetes secrets not deployed (skipping)"
fi

# Check 5: File permissions
print_status "Check 5: Checking file permissions..."

PERM_ISSUES=0

# Check for world-writable files
WORLD_WRITABLE=$(find ../../phase-5/services -type f -perm -002 2>/dev/null || true)

if [ -n "${WORLD_WRITABLE}" ]; then
    print_error "World-writable files found:"
    echo "${WORLD_WRITABLE}"
    PERM_ISSUES=1
fi

# Check for executable scripts without proper permissions
SCRIPTS=$(find ../../k8s/scripts -name "*.sh" 2>/dev/null || true)

for script in ${SCRIPTS}; do
    if [ ! -x "${script}" ]; then
        print_warning "Script not executable: ${script}"
    fi
done

if [ ${PERM_ISSUES} -eq 0 ]; then
    print_success "File permissions are correct"
fi

# Check 6: Dependencies vulnerabilities
print_status "Check 6: Checking for known vulnerabilities in dependencies..."

# Python dependencies
for requirements in $(find ../../phase-5/services -name "requirements.txt"); do
    SERVICE_DIR=$(dirname ${requirements})
    SERVICE_NAME=$(basename ${SERVICE_DIR})

    print_status "Scanning ${SERVICE_NAME} dependencies..."

    if command -v safety &>/dev/null; then
        VULNS=$(safety check -r ${requirements} --json 2>/dev/null || true)

        if [ -n "${VULNS}" ] && [ "${VULNS}" != "[]" ]; then
            print_warning "Vulnerabilities found in ${SERVICE_NAME}"
            FAILED=1
        else
            print_success "${SERVICE_NAME}: No known vulnerabilities"
        fi
    else
        print_warning "safety not installed (pip install safety)"
    fi
done

# Check 7: Container image scanning
print_status "Check 7: Checking container image security..."

if command -v trivy &>/dev/null; then
    print_status "Scanning container images with Trivy..."

    IMAGES=("chat-api:latest" "recurring-tasks:latest" "notifications:latest" "audit:latest" "frontend:latest")

    for image in "${IMAGES[@]}"; do
        print_status "Scanning ${image}..."

        VULNS=$(trivy image --severity HIGH,CRITICAL --quiet ${image} 2>/dev/null || true)

        if [ -n "${VULNS}" ]; then
            print_warning "Vulnerabilities found in ${image}"
            echo "${VULNS}" | head -10
        else
            print_success "${image}: No HIGH/CRITICAL vulnerabilities"
        fi
    done
else
    print_warning "Trivy not installed (skipping image scanning)"
fi

# Check 8: Network policies
print_status "Check 8: Checking network policies..."

if kubectl get networkpolicy -n ${NAMESPACE} &>/dev/null; then
    NP_COUNT=$(kubectl get networkpolicy -n ${NAMESPACE} --no-headers | wc -l)

    if [ ${NP_COUNT} -gt 0 ]; then
        print_success "Network policies are configured (${NP_COUNT} policies)"
    else
        print_warning "No network policies found"
    fi
else
    print_warning "Network policies not deployed"
fi

# Check 9: RBAC configuration
print_status "Check 9: Checking RBAC configuration..."

if kubectl get serviceaccount -n ${NAMESPACE} &>/dev/null; then
    # Check for default service account usage
    DEFAULT_SA_PODS=$(kubectl get pods -n ${NAMESPACE} -o jsonpath='{.items[?(@.spec.serviceAccountName=="default")].metadata.name}' 2>/dev/null || true)

    if [ -n "${DEFAULT_SA_PODS}" ]; then
        print_warning "Pods using default service account (security risk):"
        echo "${DEFAULT_SA_PODS}"
    else
        print_success "No pods using default service account"
    fi
fi

# Check 10: TLS/SSL configuration
print_status "Check 10: Checking TLS/SSL configuration..."

if kubectl get ingress -n ${NAMESPACE} &>/dev/null; then
    TLS_INGRESS=$(kubectl get ingress -n ${NAMESPACE} -o jsonpath='{.items[*].spec.tls}' 2>/dev/null || true)

    if [ -n "${TLS_INGRESS}" ] && [ "${TLS_INGRESS}" != "[]" ]; then
        print_success "TLS configured for ingress"
    else
        print_warning "TLS not configured for ingress"
    fi
fi

# Summary
echo ""
echo "========================================"
if [ ${FAILED} -eq 0 ]; then
    print_success "Security audit passed!"
    print_status "All security checks completed successfully"
    exit 0
else
    print_error "Security audit failed!"
    print_status "Please address the security issues above"
    exit 1
fi
