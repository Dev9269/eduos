.PHONY: help install test lint build-iso clean run-learnhub run-exam

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install EduOS system-wide
	sudo bash Scripts/install-eduos.sh

test: ## Run tests
	python -m pytest tests/ -v

lint: ## Run flake8 linter
	flake8 .

build-iso: ## Build EduOS ISO
	sudo bash Scripts/create-system-image.sh

clean: ## Clean Python caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

run-learnhub: ## Start Learn Hub (Flask)
	cd LearnHub && python app.py

run-exam: ## Start Exam Mode
	python ExamMode/main.py

hardening: ## Apply system hardening
	sudo bash Scripts/eduos-hardening.sh

backup: ## Create system backup
	sudo bash Scripts/create-backup.sh
