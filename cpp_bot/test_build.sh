#!/bin/bash

# Script to build and test the Telegram bot

echo "Building the Telegram bot..."
mkdir -p cmake-build-debug
cd cmake-build-debug
cmake ..
make

if [ $? -eq 0 ]; then
    echo "Build successful!"
    
    # Check if executable exists
    if [ -f "telegram_bot" ]; then
        echo "Executable 'telegram_bot' found."
        echo "To run the bot, make sure to set the required environment variables:"
        echo "export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'"
        echo "export AI_API_KEY='your_ai_api_key_here'"
        echo ""
        echo "Then run the bot with:"
        echo "cd cmake-build-debug && ./telegram_bot"
    else
        echo "Error: Executable 'telegram_bot' not found!"
    fi
else
    echo "Build failed!"
    exit 1
fi