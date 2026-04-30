# Commands
PIPENV = pipenv
PYTHON = python
APP_NAME = psgroupme
FIND = find
rm = rm
LOG_FILE = ./log/$(APP_NAME).log

# Variables 
COVERAGE_THRESHOLD ?= 40  # TODO: improve, ideally to 70-80

.PHONY: help run test lint clean

run: ## Run the app locally
	$(PIPENV) run $(PYTHON) -m $(APP_NAME) -l $(LOG_FILE)

test: ## Run tests and generate coverage reports
	$(PIPENV) run pytest tests \
	    --cov \
		--cov-report=xml \
		--cov-report=term-missing \
		--cov-fail-under=${COVERAGE_THRESHOLD}

lint: # Run linting check
	$(PIPENV) run flake8 $(APP_NAME)

clean: ## Remove temporary cache files
	$(FIND) . -type d -name "__pycache__" -exec $(RM) -rf {} +
	$(RM) -rf .pytest_cache
