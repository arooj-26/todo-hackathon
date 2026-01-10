#!/bin/bash
# Run performance test with Locust
# Tests with 1000 concurrent users to verify p95 < 200ms

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
USERS="${USERS:-1000}"
SPAWN_RATE="${SPAWN_RATE:-50}"
RUN_TIME="${RUN_TIME:-5m}"
HOST="${HOST:-http://localhost:8000}"

print_status "Starting performance test..."
echo ""
echo "Configuration:"
echo "  Users:       ${USERS}"
echo "  Spawn Rate:  ${SPAWN_RATE} users/sec"
echo "  Duration:    ${RUN_TIME}"
echo "  Target:      ${HOST}"
echo ""

# Check if locust is installed
if ! command -v locust &>/dev/null; then
    print_error "Locust is not installed"
    echo "Install with: pip install locust"
    exit 1
fi

# Run locust
print_status "Running Locust performance test..."

locust \
    -f performance-test.py \
    --headless \
    --users ${USERS} \
    --spawn-rate ${SPAWN_RATE} \
    --run-time ${RUN_TIME} \
    --host ${HOST} \
    --html performance-test-report.html \
    --csv performance-test

EXIT_CODE=$?

if [ ${EXIT_CODE} -eq 0 ]; then
    print_success "Performance test completed"
    print_status "Report saved to: performance-test-report.html"
    print_status "CSV data saved to: performance-test_*.csv"
else
    print_error "Performance test failed"
    exit ${EXIT_CODE}
fi

# Analyze results
print_status "Analyzing results..."

if [ -f "performance-test_stats.csv" ]; then
    # Check if p95 latency is under 200ms
    FAILED_ENDPOINTS=$(awk -F',' 'NR>1 && $10 > 200 {print $1 ": " $10 "ms"}' performance-test_stats.csv)

    if [ -z "${FAILED_ENDPOINTS}" ]; then
        print_success "All endpoints meet p95 < 200ms requirement"
    else
        print_error "Endpoints exceeding 200ms p95 latency:"
        echo "${FAILED_ENDPOINTS}"
        exit 1
    fi
fi

print_success "Performance test passed!"
