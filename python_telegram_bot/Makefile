# Makefile for Optical Illusion Telegram Bot

# Check if uv is available
HAS_UV := $(shell command -v uv 2> /dev/null)

# Default target
.PHONY: help install run test deploy connect

# Deploy settings (can be overridden):
#   make deploy REMOTE_DIR=/opt/na_glazok_bot
REMOTE_DIR ?= ~/na_glazok_bot
ARCHIVE_NAME ?= na_glazok_bot.tgz

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies using uv"
	@echo "  make run     - Run the Telegram bot"
	@echo "  make test    - Run tests"
	@echo "  make test-ai - Test AIService only"
	@echo "  make test-ai-debug - Test AIService with detailed logging"
	@echo "  make deploy  - Pack and upload bot to server via scp (uses .env SSH_* vars)"
	@echo "  make connect - Connect to server via ssh (uses .env SSH_* vars)"

install:
ifeq ($(HAS_UV),)
	@echo "uv not found, installing..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync
else
	@echo "Using uv to install dependencies..."
	uv sync
endif

run:
	uv run python src/main.py

test:
	uv run python test_bot.py

test-ai:
	uv run python test_ai_service.py

test-ai-debug:
	uv run python test_ai_service_debug.py

test-image:
	uv run python test_image_generation.py

deploy:
	@set -a; . ./.env; set +a; \
	set -e; \
	SSH_PORT="$${SSH_PORT:-22}"; \
	if [ -z "$$SSH_HOST" ] || [ -z "$$SSH_USERNAME" ]; then \
		echo "Error: SSH_HOST/SSH_USERNAME must be set in python_telegram_bot/.env"; \
		exit 1; \
	fi; \
	tar -czf "$(ARCHIVE_NAME)" \
		--exclude="./python_telegram_bot/$(ARCHIVE_NAME)" \
		--exclude="./python_telegram_bot/.venv" \
		--exclude="*/__pycache__" \
		--exclude="*.pyc" \
		--exclude="*.pyo" \
		--exclude="./python_telegram_bot/.pytest_cache" \
		--exclude="./python_telegram_bot/.ruff_cache" \
		--exclude="./python_telegram_bot/.mypy_cache" \
		--exclude="*.DS_Store" \
		--exclude="./python_telegram_bot/data/user_stats.db" \
		-C .. docker-compose.yml python_telegram_bot; \
	ssh -p "$$SSH_PORT" "$$SSH_USERNAME@$$SSH_HOST" "mkdir -p $(REMOTE_DIR)"; \
	scp -P "$$SSH_PORT" "$(ARCHIVE_NAME)" "$$SSH_USERNAME@$$SSH_HOST:$(REMOTE_DIR)/$(ARCHIVE_NAME)"; \
	ssh -p "$$SSH_PORT" "$$SSH_USERNAME@$$SSH_HOST" "cd $(REMOTE_DIR) && tar -xzf $(ARCHIVE_NAME) && rm -f $(ARCHIVE_NAME)"; \
	rm -f "$(ARCHIVE_NAME)"

connect:
	@set -a; . ./.env; set +a; \
	if [ -z "$$SSH_HOST" ] || [ -z "$$SSH_PORT" ] || [ -z "$$SSH_USERNAME" ]; then \
		echo "Error: SSH_HOST/SSH_PORT/SSH_USERNAME must be set in python_telegram_bot/.env"; \
		exit 1; \
	fi; \
	ssh -p "$$SSH_PORT" "$$SSH_USERNAME@$$SSH_HOST"