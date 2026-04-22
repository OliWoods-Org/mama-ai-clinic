# MAMA AI Clinic -- Build & Development Commands

.PHONY: help setup dev test safety-eval build flash clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Set up development environment
	bash scripts/setup_dev.sh

dev: ## Run Flask development server
	cd app && FLASK_APP=app:create_app FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=5000

test: ## Run all tests
	cd app && python -m pytest ../tests/ -v

safety-eval: ## Run safety evaluation (red-line cases)
	cd app && python -m eval.safety_eval

benchmark: ## Run inference benchmark on device
	bash inference/benchmark.sh

build: ## Build SD card image
	bash image/build.sh

flash: ## Flash image to SD card (usage: make flash DEVICE=/dev/sdX)
	bash image/flash.sh output/mama-ai-clinic-*.img.xz $(DEVICE)

download-model: ## Download the default model
	bash inference/download_model.sh

validate-knowledge: ## Validate knowledge base JSON files
	python scripts/validate_knowledge.py

clean: ## Remove build artifacts
	rm -rf build/ output/ venv/ __pycache__/ .pytest_cache/
