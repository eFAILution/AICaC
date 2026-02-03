# AICaC Validation Makefile
# Run `make help` for available commands

.PHONY: help setup test measure clean prepare

help:
	@echo "AICaC Validation Framework"
	@echo ""
	@echo "Setup:"
	@echo "  make setup            Install dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make prepare          Create test variants from sample project"
	@echo "  make measure          Run token measurement (reality only)"
	@echo "  make measure-all      Run with selective loading comparison"
	@echo "  make measure-full     Full experiment (30 trials, all modes)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove generated files"
	@echo ""
	@echo "Note: Results show BOTH the reality (more tokens) AND"
	@echo "      the potential (fewer tokens with tool evolution)"

setup:
	pip install -r validation/requirements.txt

prepare:
	@echo "Creating test variants..."
	@mkdir -p experiments
	@rm -rf experiments/aicac-full experiments/agents-only experiments/readme-only
	@cp -r validation/examples/sample-project experiments/aicac-full
	@cp -r validation/examples/sample-project experiments/agents-only
	@cp -r validation/examples/sample-project experiments/readme-only
	@rm -f experiments/readme-only/AGENTS.md
	@rm -rf experiments/readme-only/.ai/
	@rm -rf experiments/agents-only/.ai/
	@echo ""
	@echo "Created 3 variants in experiments/"
	@echo "  readme-only  : README.md only"
	@echo "  agents-only  : README.md + AGENTS.md"
	@echo "  aicac-full   : README.md + AGENTS.md + .ai/"

# Reality check: what happens with current AI tools
measure: prepare
	@echo ""
	@echo "Running token measurement (current AI tool reality)..."
	@echo ""
	cd validation/scripts && python token_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--all-formats \
		--trials 5 \
		--output ../../experiments/results.json

# Include selective loading comparison
measure-all: prepare
	@echo ""
	@echo "Running token measurement (reality + selective comparison)..."
	@echo ""
	cd validation/scripts && python token_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--all-formats \
		--include-selective \
		--trials 5 \
		--output ../../experiments/results.json

# Full statistical experiment
measure-full: prepare
	@echo ""
	@echo "Running full experiment (30 trials, all modes)..."
	@echo ""
	cd validation/scripts && python token_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--all-formats \
		--include-selective \
		--trials 30 \
		--output ../../experiments/full_results.json

clean:
	rm -rf experiments/
	rm -rf __pycache__ validation/scripts/__pycache__
	rm -rf .pytest_cache
