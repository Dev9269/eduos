PYTHON ?= python3
VENV_BIN ?= $(shell command -v python3 >/dev/null 2>&1 && echo python3)

.PHONY: help install test test-security test-e2e lint validate clean \
        build build-freebsd-iso run-server run-admin run-learnhub run-exam \
        run-welcome token backup

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------- Validation ----------

test: ## Run the full test suite
	$(PYTHON) -m pytest tests/ -v

test-security: ## Run the security test suite only
	$(PYTHON) -m pytest tests/test_security.py -v

test-e2e: ## Run the end-to-end exam flow suite
	$(PYTHON) -m pytest tests/test_exam_flow.py -v

lint: ## Lint all Python files with pyflakes
	$(PYTHON) -m pyflakes . 2>/dev/null || find . -name "*.py" -not -path "./.git/*" -not -path "*/__pycache__/*" -print0 | xargs -0 $(PYTHON) -m pyflakes || true

validate: test ## Full pre-build validation (tests + compile + config checks)
	@echo "== py_compile all Python files =="
	@find . -name "*.py" -not -path "./.git/*" -not -path "*/__pycache__/*" -print0 | xargs -0 $(PYTHON) -m py_compile
	@echo "== YAML workflow validation =="
	@$(PYTHON) -c "import glob, yaml, sys; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]; print('workflows: OK')"
	@echo "== Shell syntax checks =="
	@for f in Scripts/*.sh Services/freebsd/*; do sh -n "$$f" && echo "  $$f OK"; done
	@echo "== FreeBSD package list validation =="
	@$(PYTHON) -c "import sys; lines=[l.strip() for l in open('Packages/freebsd-packages.txt') if l.strip() and not l.startswith('#')]; assert lines, 'empty package list'; print(f'  {len(lines)} entries OK')"
	@echo "Validation complete."

# ---------- Build ----------

build: ## Stage package trees and run validation
	bash Scripts/build.sh

build-freebsd-iso: ## Trigger the FreeBSD ISO build on GitHub Actions
	gh workflow run build-freebsd-iso.yml

# ---------- Runtime ----------

run-server: ## Start the central EduOS server
	$(PYTHON) Server/eduos_server.py

run-admin: ## Start the Admin Center
	$(PYTHON) AdminCenter/eduos_admin.py

run-learnhub: ## Start the Learn Hub web app
	$(PYTHON) LearnHub/learnhub_app.py

run-exam: ## Start Exam Mode
	$(PYTHON) ExamMode/exam_app.py

run-welcome: ## Launch the first-login welcome wizard
	$(PYTHON) Scripts/eduos-welcome.py

token: ## Generate an admin API token
	$(PYTHON) Server/generate-admin-token.py

# ---------- Maintenance ----------

install: ## Install EduOS system-wide (FreeBSD rc.d / Linux systemd)
	sudo sh Scripts/install-eduos.sh

clean: ## Clean Python build caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist build 2>/dev/null || true

backup: ## Create a timestamped backup tarball of the repo
	@mkdir -p backups
	tar -czf backups/eduos-backup-$$(date +%Y%m%d-%H%M%S).tar.gz \
		--exclude=.git --exclude=__pycache__ --exclude=.pytest_cache .
	@echo "Backup written to backups/"
