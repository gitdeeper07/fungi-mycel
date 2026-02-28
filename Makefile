# 🍄 FUNGI-MYCEL Makefile
# Mycelial Network Intelligence Framework
# Version: 1.0.0

.PHONY: help install dev test clean build docker run docs release all

# Colors for terminal output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Project variables
PROJECT_NAME = fungi-mycel
VERSION = 1.0.0
PYTHON = python3
PIP = pip3
VENV_DIR = .venv
DOCKER_IMAGE = gitlab.com/gitdeeper07/fungi-mycel
DOCKER_TAG = latest
PORT_API = 8000
PORT_DASHBOARD = 8501
PORT_METRICS = 9090

# -----------------------------------------------------------------------------
# Help target
help:
	@echo "$(PURPLE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(PURPLE)║                    🍄 FUNGI-MYCEL Makefile                     ║$(NC)"
	@echo "$(PURPLE)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)Available targets:$(NC)"
	@echo ""
	@echo "$(GREEN)Installation & Setup:$(NC)"
	@echo "  $(YELLOW)make install$(NC)        - Install package in development mode"
	@echo "  $(YELLOW)make venv$(NC)           - Create virtual environment"
	@echo "  $(YELLOW)make requirements$(NC)   - Install requirements from file"
	@echo "  $(YELLOW)make dev-deps$(NC)        - Install development dependencies"
	@echo "  $(YELLOW)make all-deps$(NC)        - Install all dependencies"
	@echo ""
	@echo "$(GREEN)Testing & Quality:$(NC)"
	@echo "  $(YELLOW)make test$(NC)           - Run all tests"
	@echo "  $(YELLOW)make test-unit$(NC)       - Run unit tests only"
	@echo "  $(YELLOW)make test-integration$(NC) - Run integration tests only"
	@echo "  $(YELLOW)make test-hypothesis$(NC) - Run hypothesis tests (H1-H8)"
	@echo "  $(YELLOW)make test-benchmark$(NC)  - Run benchmarks"
	@echo "  $(YELLOW)make coverage$(NC)        - Run tests with coverage report"
	@echo "  $(YELLOW)make lint$(NC)           - Run linters (ruff, flake8)"
	@echo "  $(YELLOW)make format$(NC)         - Format code (black, isort)"
	@echo "  $(YELLOW)make type-check$(NC)      - Run mypy type checking"
	@echo "  $(YELLOW)make security$(NC)        - Run security checks (bandit)"
	@echo "  $(YELLOW)make pre-commit$(NC)      - Run all pre-commit hooks"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  $(YELLOW)make run-api$(NC)        - Run API server"
	@echo "  $(YELLOW)make run-dashboard$(NC)   - Run dashboard"
	@echo "  $(YELLOW)make run-all$(NC)         - Run all services"
	@echo "  $(YELLOW)make jupyter$(NC)         - Start Jupyter notebook"
	@echo "  $(YELLOW)make shell$(NC)           - Open Python shell"
	@echo "  $(YELLOW)make ipython$(NC)         - Open IPython shell"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  $(YELLOW)make docs$(NC)           - Build documentation"
	@echo "  $(YELLOW)make docs-serve$(NC)      - Serve documentation locally"
	@echo "  $(YELLOW)make docs-clean$(NC)      - Clean documentation build"
	@echo "  $(YELLOW)make docs-pdf$(NC)        - Build PDF documentation"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  $(YELLOW)make docker-build$(NC)    - Build Docker image"
	@echo "  $(YELLOW)make docker-run$(NC)      - Run Docker container"
	@echo "  $(YELLOW)make docker-dev$(NC)      - Run development container"
	@echo "  $(YELLOW)make docker-ml$(NC)       - Run ML container with GPU"
	@echo "  $(YELLOW)make docker-push$(NC)     - Push Docker image to registry"
	@echo "  $(YELLOW)make docker-compose-up$(NC) - Start docker-compose services"
	@echo "  $(YELLOW)make docker-compose-down$(NC) - Stop docker-compose services"
	@echo "  $(YELLOW)make docker-clean$(NC)     - Clean Docker artifacts"
	@echo ""
	@echo "$(GREEN)Data & Analysis:$(NC)"
	@echo "  $(YELLOW)make demo$(NC)            - Run demo with sample data"
	@echo "  $(YELLOW)make validate$(NC)        - Validate dataset"
	@echo "  $(YELLOW)make correlate$(NC)        - Check parameter correlations"
	@echo "  $(YELLOW)make stats$(NC)           - Generate statistics"
	@echo "  $(YELLOW)make alerts$(NC)          - Check active alerts"
	@echo ""
	@echo "$(GREEN)Deployment:$(NC)"
	@echo "  $(YELLOW)make build$(NC)           - Build distribution packages"
	@echo "  $(YELLOW)make clean$(NC)           - Clean build artifacts"
	@echo "  $(YELLOW)make distclean$(NC)        - Deep clean (including venv)"
	@echo "  $(YELLOW)make release$(NC)          - Create release"
	@echo "  $(YELLOW)make publish-pypi$(NC)     - Publish to PyPI"
	@echo "  $(YELLOW)make publish-testpypi$(NC) - Publish to TestPyPI"
	@echo "  $(YELLOW)make deploy-netlify$(NC)   - Deploy dashboard to Netlify"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  $(YELLOW)make version$(NC)         - Show version"
	@echo "  $(YELLOW)make info$(NC)            - Show system information"
	@echo "  $(YELLOW)make doctor$(NC)           - Run diagnostics"
	@echo "  $(YELLOW)make update$(NC)           - Update dependencies"
	@echo "  $(YELLOW)make backup$(NC)           - Backup data"
	@echo "  $(YELLOW)make restore$(NC)          - Restore data"
	@echo ""
	@echo "$(CYAN)Examples:$(NC)"
	@echo "  make install && make test"
	@echo "  make docker-build && make docker-run"
	@echo "  make docs-serve && open http://localhost:8000"
	@echo ""

# -----------------------------------------------------------------------------
# Installation & Setup
venv:
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)Activate with: source $(VENV_DIR)/bin/activate$(NC)"

install: venv
	@echo "$(GREEN)Installing package in development mode...$(NC)"
	. $(VENV_DIR)/bin/activate && $(PIP) install -e .

requirements:
	@echo "$(GREEN)Installing requirements...$(NC)"
	. $(VENV_DIR)/bin/activate && $(PIP) install -r requirements.txt

dev-deps:
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	. $(VENV_DIR)/bin/activate && $(PIP) install -e ".[dev]"

all-deps:
	@echo "$(GREEN)Installing all dependencies...$(NC)"
	. $(VENV_DIR)/bin/activate && $(PIP) install -e ".[all]"

# -----------------------------------------------------------------------------
# Testing & Quality
test:
	@echo "$(GREEN)Running all tests...$(NC)"
	. $(VENV_DIR)/bin/activate && pytest tests/ -v

test-unit:
	@echo "$(GREEN)Running unit tests...$(NC)"
	. $(VENV_DIR)/bin/activate && pytest tests/unit/ -v

test-integration:
	@echo "$(GREEN)Running integration tests...$(NC)"
	. $(VENV_DIR)/bin/activate && pytest tests/integration/ -v

test-hypothesis:
	@echo "$(GREEN)Running hypothesis tests (H1-H8)...$(NC)"
	. $(VENV_DIR)/bin/activate && pytest tests/hypothesis/ -v

test-benchmark:
	@echo "$(GREEN)Running benchmarks...$(NC)"
	. $(VENV_DIR)/bin/activate && pytest tests/benchmarks/ --benchmark-only

coverage:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	. $(VENV_DIR)/bin/activate && pytest --cov=fungi_mycel --cov-report=html --cov-report=term

lint:
	@echo "$(GREEN)Running linters...$(NC)"
	. $(VENV_DIR)/bin/activate && ruff check fungi_mycel/
	. $(VENV_DIR)/bin/activate && flake8 fungi_mycel/

format:
	@echo "$(GREEN)Formatting code...$(NC)"
	. $(VENV_DIR)/bin/activate && black fungi_mycel/ tests/
	. $(VENV_DIR)/bin/activate && isort fungi_mycel/ tests/

type-check:
	@echo "$(GREEN)Running type checking...$(NC)"
	. $(VENV_DIR)/bin/activate && mypy fungi_mycel/

security:
	@echo "$(GREEN)Running security checks...$(NC)"
	. $(VENV_DIR)/bin/activate && bandit -r fungi_mycel/ -c pyproject.toml

pre-commit:
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	. $(VENV_DIR)/bin/activate && pre-commit run --all-files

# -----------------------------------------------------------------------------
# Development
run-api:
	@echo "$(GREEN)Starting API server on port $(PORT_API)...$(NC)"
	. $(VENV_DIR)/bin/activate && fungi-mycel serve --api --host 0.0.0.0 --port $(PORT_API)

run-dashboard:
	@echo "$(GREEN)Starting dashboard on port $(PORT_DASHBOARD)...$(NC)"
	. $(VENV_DIR)/bin/activate && fungi-mycel serve --dashboard --host 0.0.0.0 --port $(PORT_DASHBOARD)

run-all:
	@echo "$(GREEN)Starting all services...$(NC)"
	. $(VENV_DIR)/bin/activate && fungi-mycel serve --all --host 0.0.0.0

jupyter:
	@echo "$(GREEN)Starting Jupyter notebook...$(NC)"
	. $(VENV_DIR)/bin/activate && jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser

shell:
	@echo "$(GREEN)Opening Python shell...$(NC)"
	. $(VENV_DIR)/bin/activate && python

ipython:
	@echo "$(GREEN)Opening IPython shell...$(NC)"
	. $(VENV_DIR)/bin/activate && ipython

# -----------------------------------------------------------------------------
# Documentation
docs:
	@echo "$(GREEN)Building documentation...$(NC)"
	. $(VENV_DIR)/bin/activate && cd docs && make html

docs-serve:
	@echo "$(GREEN)Serving documentation at http://localhost:8000...$(NC)"
	. $(VENV_DIR)/bin/activate && cd docs/build/html && python -m http.server 8000

docs-clean:
	@echo "$(GREEN)Cleaning documentation...$(NC)"
	cd docs && make clean

docs-pdf:
	@echo "$(GREEN)Building PDF documentation...$(NC)"
	. $(VENV_DIR)/bin/activate && cd docs && make latexpdf

# -----------------------------------------------------------------------------
# Docker
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:
	@echo "$(GREEN)Running Docker container...$(NC)"
	docker run -p $(PORT_DASHBOARD):$(PORT_DASHBOARD) -p $(PORT_API):$(PORT_API) $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-dev:
	@echo "$(GREEN)Running development container...$(NC)"
	docker run -it -v $$(pwd):/opt/fungi-mycel -p 8888:8888 $(DOCKER_IMAGE):$(DOCKER_TAG) /bin/bash

docker-ml:
	@echo "$(GREEN)Running ML container with GPU...$(NC)"
	docker run --gpus all -p $(PORT_API):$(PORT_API) $(DOCKER_IMAGE):ml

docker-push:
	@echo "$(GREEN)Pushing Docker image...$(NC)"
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-compose-up:
	@echo "$(GREEN)Starting docker-compose services...$(NC)"
	docker-compose up -d

docker-compose-down:
	@echo "$(GREEN)Stopping docker-compose services...$(NC)"
	docker-compose down

docker-clean:
	@echo "$(GREEN)Cleaning Docker artifacts...$(NC)"
	docker system prune -f

# -----------------------------------------------------------------------------
# Data & Analysis
demo:
	@echo "$(GREEN)Running demo with sample data...$(NC)"
	. $(VENV_DIR)/bin/activate && python scripts/mnis_demo.py --site bialowieza-01

validate:
	@echo "$(GREEN)Validating dataset...$(NC)"
	. $(VENV_DIR)/bin/activate && python scripts/validate_dataset.py --sites 39 --mnus 2648

correlate:
	@echo "$(GREEN)Checking parameter correlations...$(NC)"
	. $(VENV_DIR)/bin/activate && python scripts/check_correlation.py --param1 rho-e --param2 k-topo

stats:
	@echo "$(GREEN)Generating statistics...$(NC)"
	. $(VENV_DIR)/bin/activate && python scripts/generate_stats.py

alerts:
	@echo "$(GREEN)Checking active alerts...$(NC)"
	. $(VENV_DIR)/bin/activate && fungi-mycel alerts --status active

# -----------------------------------------------------------------------------
# Deployment
build:
	@echo "$(GREEN)Building distribution packages...$(NC)"
	. $(VENV_DIR)/bin/activate && python -m build

clean:
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage_html/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf *.log
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

distclean: clean
	@echo "$(GREEN)Deep cleaning...$(NC)"
	rm -rf $(VENV_DIR)/
	rm -rf .venv/
	rm -rf .env/
	rm -rf .tox/
	rm -rf .eggs/

release:
	@echo "$(GREEN)Creating release v$(VERSION)...$(NC)"
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)

publish-pypi:
	@echo "$(GREEN)Publishing to PyPI...$(NC)"
	. $(VENV_DIR)/bin/activate && twine upload dist/*

publish-testpypi:
	@echo "$(GREEN)Publishing to TestPyPI...$(NC)"
	. $(VENV_DIR)/bin/activate && twine upload --repository-url https://test.pypi.org/legacy/ dist/*

deploy-netlify:
	@echo "$(GREEN)Deploying to Netlify...$(NC)"
	cd dashboard && netlify deploy --prod

# -----------------------------------------------------------------------------
# Utilities
version:
	@echo "$(GREEN)FUNGI-MYCEL v$(VERSION)$(NC)"
	@echo "MNIS Accuracy: 91.8%"
	@echo "Dataset: 2,648 MNUs · 39 sites · 5 biomes"

info:
	@echo "$(GREEN)System Information:$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "OS: $$(uname -a)"
	@echo "Memory: $$(free -h | grep Mem | awk '{print $$2}')"
	@echo "Disk: $$(df -h . | tail -1 | awk '{print $$4}')"

doctor:
	@echo "$(GREEN)Running diagnostics...$(NC)"
	. $(VENV_DIR)/bin/activate && fungi-mycel doctor

update:
	@echo "$(GREEN)Updating dependencies...$(NC)"
	. $(VENV_DIR)/bin/activate && $(PIP) install --upgrade -r requirements.txt

backup:
	@echo "$(GREEN)Backing up data...$(NC)"
	@mkdir -p backups
	tar -czf backups/fungi_mycel_backup_$$(date +%Y%m%d_%H%M%S).tar.gz data/ config/ *.md

restore:
	@echo "$(GREEN)Restoring from backup...$(NC)"
	@echo "Usage: make restore FILE=backup.tar.gz"
	tar -xzf $(FILE)

# -----------------------------------------------------------------------------
# Default target
all: install test docs build
	@echo "$(GREEN)All targets completed successfully!$(NC)"

# -----------------------------------------------------------------------------
# Include additional makefiles if they exist
-include Makefile.local

# -----------------------------------------------------------------------------
# Help message when no target is specified
.DEFAULT_GOAL = help
