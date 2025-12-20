#!/bin/bash

# Script to run the Telegram bot with default credentials
# For production use, please set your own TELEGRAM_BOT_TOKEN and AI_API_KEY

echo "Setting environment variables..."
export TELEGRAM_BOT_TOKEN="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
export AI_API_KEY="sk-aitunnel-..."

echo "Starting Telegram bot..."
echo "Press Ctrl+C to stop the bot"
cd cmake-build-debug && ./telegram_bot