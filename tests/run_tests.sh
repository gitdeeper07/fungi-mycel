#!/bin/bash

# FUNGI-MYCEL Test Runner
# =======================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   FUNGI-MYCEL Test Suite Runner       ${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Function to run tests with header
run_test_suite() {
    echo -e "\n${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}   $1${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    
    if [ -z "$2" ]; then
        pytest $3 -v
    else
        pytest $2 -v
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 passed${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        FAILED=1
    fi
}

FAILED=0

# Parse arguments
if [ "$1" == "all" ] || [ -z "$1" ]; then
    # Run all test suites
    run_test_suite "Unit Tests" "tests/unit/"
    run_test_suite "Integration Tests" "tests/integration/"
    run_test_suite "Hypothesis Tests (H1-H8)" "tests/hypothesis/"
    run_test_suite "Benchmark Tests" "tests/benchmarks/"

elif [ "$1" == "unit" ]; then
    run_test_suite "Unit Tests" "tests/unit/"

elif [ "$1" == "integration" ]; then
    run_test_suite "Integration Tests" "tests/integration/"

elif [ "$1" == "hypothesis" ]; then
    run_test_suite "Hypothesis Tests (H1-H8)" "tests/hypothesis/"

elif [ "$1" == "benchmark" ]; then
    run_test_suite "Benchmark Tests" "tests/benchmarks/"

elif [ "$1" == "quick" ]; then
    run_test_suite "Quick Tests (No Benchmarks)" "tests/unit/ tests/integration/ tests/hypothesis/"

elif [ "$1" == "h1" ]; then
    run_test_suite "Hypothesis H1 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h1_accuracy"
elif [ "$1" == "h2" ]; then
    run_test_suite "Hypothesis H2 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h2_rho_e_ktopo_correlation"
elif [ "$1" == "h3" ]; then
    run_test_suite "Hypothesis H3 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h3_eta_nw_variation"
elif [ "$1" == "h4" ]; then
    run_test_suite "Hypothesis H4 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h4_ser_deviation"
elif [ "$1" == "h5" ]; then
    run_test_suite "Hypothesis H5 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h5_grad_c_accuracy"
elif [ "$1" == "h6" ]; then
    run_test_suite "Hypothesis H6 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h6_abi_amplification"
elif [ "$1" == "h7" ]; then
    run_test_suite "Hypothesis H7 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h7_bfs_correlation"
elif [ "$1" == "h8" ]; then
    run_test_suite "Hypothesis H8 Only" "tests/hypothesis/test_hypotheses.py::TestHypotheses::test_h8_ensemble_improvement"

elif [ "$1" == "coverage" ]; then
    echo -e "\n${BLUE}Running tests with coverage...${NC}"
    pytest --cov=fungi_mycel --cov-report=term --cov-report=html tests/
    echo -e "\n${GREEN}Coverage report generated in htmlcov/${NC}"

elif [ "$1" == "help" ]; then
    echo "Usage: ./run_tests.sh [option]"
    echo ""
    echo "Options:"
    echo "  all         Run all tests (default)"
    echo "  unit        Run unit tests only"
    echo "  integration Run integration tests only"
    echo "  hypothesis  Run hypothesis tests (H1-H8)"
    echo "  benchmark   Run benchmark tests"
    echo "  quick       Run all except benchmarks"
    echo "  h1-h8       Run specific hypothesis test"
    echo "  coverage    Run tests with coverage report"
    echo "  help        Show this help"

else
    echo -e "${RED}Unknown option: $1${NC}"
    ./run_tests.sh help
    exit 1
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All test suites passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed.${NC}"
fi
echo -e "${BLUE}========================================${NC}"

exit $FAILED
