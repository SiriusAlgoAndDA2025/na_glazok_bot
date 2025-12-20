# Optical Illusion Telegram Bot

This Telegram bot generates optical illusion images with two objects and asks users to determine which is larger. It integrates with AI services to create prompts and generate images.

## Features

- Generate optical illusion challenges with AI
- Three answer options: "First is larger", "Second is larger", "They are equal"
- Immediate feedback on user responses
- Preserves existing functionality including `/image_url` command

## Commands

- `/start` - Welcome message and command list
- `/help` - Show available commands
- `/illusion` - Generate a new optical illusion challenge
- `/image_url` - Send a sample image (existing functionality preserved)

## Implementation Details

### Components

1. **AIService** - Handles communication with AI APIs
   - Prompt generation using deepseek-v3.2 model
   - Image generation using gpt-image-1.5-low model

2. **GameLogic** - Manages game state and challenges
   - Tracks active challenges for users
   - Validates user answers
   - Handles challenge timeouts

3. **TelegramBot** - Main bot implementation
   - Processes user commands
   - Sends images with interactive buttons
   - Handles user responses

### AI Integration

The bot integrates with aitunnel.ru APIs:

1. **Prompt Generation API**
   - Endpoint: `https://api.aitunnel.ru/v1/chat/completions`
   - Model: `deepseek-v3.2`
   - Generates prompts for optical illusions with correct answers

2. **Image Generation API**
   - Endpoint: `https://api.aitunnel.ru/v1/images/generations`
   - Model: `gpt-image-1.5-low`
   - Generates images based on prompts


### Building

You can build the project in several ways:

1. Using the build script (recommended):
```bash
./build_and_run.sh
```

2. Using the test build script:
```bash
./test_build.sh
```

3. Manual build:
```bash
mkdir cmake-build-debug
cd cmake-build-debug
cmake ..
make
```

### Configuration

Set your API keys as environment variables:
- `TELEGRAM_BOT_TOKEN` for your Telegram bot token
- `AI_API_KEY` for your AI service API key

Example:
```bash
export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'
export AI_API_KEY='your_ai_api_key_here'
```
## Dependencies

- Boost.Beast
- nlohmann/json
- OpenSSL

## Usage

1. Build the project using one of the methods above
2. Set your API keys in environment variables:
```bash
export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'
export AI_API_KEY='your_ai_api_key_here'
```

### Quick Start
For quick testing with the default credentials, you can use:
```bash
./run_bot.sh
```

3. Run the bot with `./cmake-build-debug/telegram_bot` or `./build_and_run.sh`
4. Use `/illusion` command in Telegram to generate optical illusion challenges