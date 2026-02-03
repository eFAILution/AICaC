# AICaC Validation Makefile
# Run `make help` for available commands

.PHONY: help setup test measure clean prepare-variants

# Default target
help:
	@echo "AICaC Validation Framework"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          Install dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make prepare        Create test variants from sample project"
	@echo "  make measure        Run token measurement (quick, 5 trials)"
	@echo "  make measure-full   Run full experiment (30 trials)"
	@echo "  make analyze        Analyze results"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          Remove generated files"
	@echo "  make format         Format Python code"
	@echo ""
	@echo "Environment variables:"
	@echo "  ANTHROPIC_API_KEY   Required for Claude token counting"

# Install dependencies
setup:
	pip install -r validation/requirements.txt

# Prepare test variants from sample project
prepare:
	@echo "Creating test variants..."
	@mkdir -p experiments
	@cp -r validation/examples/sample-project experiments/aicac-full
	@cp -r validation/examples/sample-project experiments/agents-only
	@cp -r validation/examples/sample-project experiments/readme-only
	@rm -f experiments/readme-only/AGENTS.md
	@rm -rf experiments/readme-only/.ai/
	@rm -rf experiments/agents-only/.ai/
	@echo "Created 3 variants in experiments/"
	@echo "  - experiments/readme-only  (README.md only)"
	@echo "  - experiments/agents-only  (README.md + AGENTS.md)"
	@echo "  - experiments/aicac-full   (README.md + AGENTS.md + .ai/)"

# Quick token measurement (5 trials)
measure: prepare
	@echo "Running token measurement (5 trials)..."
	cd validation/scripts && python token_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--all-formats \
		--trials 5 \
		--output ../../experiments/results.json
	@echo "Results saved to experiments/results.json"

# Full experiment (30 trials)
measure-full: prepare
	@echo "Running full experiment (30 trials)..."
	cd validation/scripts && python token_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--all-formats \
		--trials 30 \
		--output ../../experiments/full_results.json
	@echo "Results saved to experiments/full_results.json"

# Analyze results
analyze:
	@if [ -f experiments/results.json ]; then \
		echo "Analyzing results..."; \
		cd validation/scripts && python -c "import json; \
			data = json.load(open('../../experiments/results.json')); \
			print('\\nResults Summary:'); \
			print(json.dumps(data.get('summary', data), indent=2))"; \
	else \
		echo "No results found. Run 'make measure' first."; \
	fi

# Clean generated files
clean:
	rm -rf experiments/
	rm -f validation/scripts/*.pyc
	rm -rf validation/scripts/__pycache__/
	rm -rf .pytest_cache/

# Format Python code
format:
	black validation/scripts/

# Run tests (if any exist)
test:
	@echo "Running validation script tests..."
	cd validation/scripts && python -c "import token_measurement; print('Import OK')"
	@echo "Basic validation passed"
