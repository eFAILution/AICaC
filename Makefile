# AICaC Validation Makefile
# Run `make help` for available commands

.PHONY: help setup test measure clean prepare

help:
	@echo "AICaC Validation Framework"
	@echo ""
	@echo "Setup:"
	@echo "  make setup            Install dependencies"
	@echo ""
	@echo "Token Measurement (free):"
	@echo "  make prepare          Create test variants from sample project"
	@echo "  make measure          Run token measurement (reality only)"
	@echo "  make measure-all      Run with selective loading comparison"
	@echo "  make measure-full     Full experiment (30 trials, all modes)"
	@echo ""
	@echo "Performance Measurement (uses AI API - costs money):"
	@echo "  make perf-estimate    Show cost estimate (no API calls)"
	@echo "  make perf-ollama      Run with Ollama (FREE, local)"
	@echo "  make perf-claude      Run with Claude (requires ANTHROPIC_API_KEY)"
	@echo "  make perf-openai      Run with OpenAI (requires OPENAI_API_KEY)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove generated files"

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

# Performance measurement (uses AI APIs)
perf-estimate: prepare
	@cd validation/scripts && python performance_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--estimate-cost

perf-ollama: prepare
	@echo "Running performance test with Ollama (free, local)..."
	@cd validation/scripts && python performance_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--provider ollama \
		--trials 5 \
		--output ../../experiments/perf_ollama.json

perf-claude: prepare
	@echo "Running performance test with Claude (requires ANTHROPIC_API_KEY)..."
	@cd validation/scripts && python performance_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--provider anthropic \
		--trials 3 \
		--output ../../experiments/perf_claude.json

perf-openai: prepare
	@echo "Running performance test with OpenAI (requires OPENAI_API_KEY)..."
	@cd validation/scripts && python performance_measurement.py \
		--repo-path ../../experiments/aicac-full \
		--provider openai \
		--trials 3 \
		--output ../../experiments/perf_openai.json

clean:
	rm -rf experiments/
	rm -rf __pycache__ validation/scripts/__pycache__
	rm -rf .pytest_cache
