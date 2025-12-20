#!/bin/bash

# Build and run script for Telegram Bot
# This script compiles the project and runs the bot

# Check if required environment variables are set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Error: TELEGRAM_BOT_TOKEN environment variable is not set"
    echo "Please set it with: export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'"
    exit 1
fi

if [ -z "$AI_API_KEY" ]; then
    echo "Error: AI_API_KEY environment variable is not set"
    echo "Please set it with: export AI_API_KEY='your_ai_api_key_here'"
    exit 1
fi

echo "Building Telegram Bot..."
mkdir -p cmake-build-debug
cd cmake-build-debug
cmake .. -G "Unix Makefiles"
make

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Starting Telegram Bot..."
    echo "Press Ctrl+C to stop the bot"
    ./telegram_bot
else
    echo "Build failed!"
    exit 1
fi