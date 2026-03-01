.PHONY: install install-browsers test test-api test-db test-ui test-robot test-smoke test-all report clean help

PYTHON   := python3
PIP      := pip3
PYTEST   := pytest
ROBOT    := python -m robot
ALLURE   := allure
REPORTS  := reports

install:
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt

install-browsers:
	@echo "Installing Playwright browsers..."
	playwright install chromium firefox --with-deps

setup: install install-browsers
	@echo "Setup complete."

test-smoke:
	$(PYTEST) tests/api/ tests/database/ tests/ui/ -m smoke -v --tb=short --alluredir=$(REPORTS)/allure-results

test-api:
	$(PYTEST) tests/api/ -v --tb=short --alluredir=$(REPORTS)/allure-results --junitxml=$(REPORTS)/api-junit.xml

test-db:
	$(PYTEST) tests/database/ -v --tb=short --alluredir=$(REPORTS)/allure-results --junitxml=$(REPORTS)/db-junit.xml

test-ui:
	$(PYTEST) tests/ui/ -v --tb=short --alluredir=$(REPORTS)/allure-results --junitxml=$(REPORTS)/ui-junit.xml

test-ui-headed:
	$(PYTEST) tests/ui/ -v --tb=short --headed --alluredir=$(REPORTS)/allure-results

test-robot:
	$(ROBOT) --outputdir $(REPORTS)/robot --loglevel DEBUG tests/robot/api_smoke.robot tests/robot/booking_smoke.robot

test-all: test-api test-db test-robot test-ui

test-parallel:
	$(PYTEST) tests/api/ tests/database/ -n 4 -v --tb=short --alluredir=$(REPORTS)/allure-results

report:
	$(ALLURE) generate $(REPORTS)/allure-results --clean -o $(REPORTS)/allure-html
	$(ALLURE) open $(REPORTS)/allure-html

clean:
	rm -rf $(REPORTS)/allure-results $(REPORTS)/allure-html $(REPORTS)/robot $(REPORTS)/*.xml $(REPORTS)/*.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

help:
	@echo "Commands: setup | test-smoke | test-api | test-db | test-ui | test-robot | test-all | report | clean"
