# Optical Illusion Telegram Bot (Python Implementation)

This Telegram bot generates optical illusion images with two objects and asks users to determine which is larger. It integrates with AI services to create prompts and generate images.

## Features

- Generate optical illusion challenges with AI
- Three answer options: "First is larger", "Second is larger", "They are equal"
- Immediate feedback on user responses
- User-friendly menu interface with buttons
- Persistent user statistics saved to disk
- Random illusion gallery from user-maintained collection
- Preserves existing functionality including `/image_url` command

## Commands

- `/start` - Welcome message and main menu
- `/help` - Show available commands and help information
- `/illusion` - Generate a new optical illusion challenge
- `/stats` - View your statistics
- `/image_url` - Send a sample image (existing functionality preserved)

## Menu Options

- 🔮 Generate Illusion - Create a new optical illusion challenge
- 🎲 Random Illusion - Get a random illusion from our collection
- 📊 View Statistics - Show your performance stats
- ℹ️ Help - Show help information

## Implementation Details

### Components

1. **AIService** - Handles communication with AI APIs
   - Prompt generation using deepseek-r1 model
   - Image generation using gpt-image-1 model

2. **GameLogic** - Manages game state and challenges
   - Tracks active challenges for users
   - Validates user answers
   - Handles challenge timeouts
   - Saves/loads user statistics to/from disk in the `data/` directory

3. **TelegramBot** - Main bot implementation
   - Processes user commands
   - Sends images with interactive buttons
   - Handles user responses
   - Manages random illusion gallery from `data/illusion_urls.txt`

### AI Integration

The bot integrates with aitunnel.ru APIs:

1. **Prompt Generation API**
   - Endpoint: `https://api.aitunnel.ru/v1/chat/completions`
   - Model: `deepseek-r1`
   - Generates prompts for optical illusions with correct answers

2. **Image Generation API**
   - Endpoint: `https://api.aitunnel.ru/v1/images/generations`
   - Model: `gpt-image-1`
   - Generates images based on prompts

## Installation

1. Install dependencies using uv:
   ```bash
   make install
   ```

2. Set your API keys in a `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   AI_API_KEY=your_ai_api_key_here
   ```

## Usage

1. Run the bot:
   ```bash
   make run
   ```

2. Start a conversation with the bot using the `/start` command

3. Use the menu buttons to navigate:
   - 🔮 Generate Illusion - Create a new optical illusion challenge
   - 📊 View Statistics - Show your performance stats
   - ℹ️ Help - Show help information

4. Alternatively, you can use the traditional commands:
   - `/illusion` - Generate a new optical illusion challenge
   - `/stats` - View your statistics
   - `/help` - Show help information

## Makefile Commands

- `make install` - Install dependencies using uv
- `make run` - Run the Telegram bot
- `make test` - Run tests
- `make test-image` - Run image generation test

## Environment Variables

The bot uses the following environment variables:

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `AI_API_KEY` - Your AI service API key
- `PROMPT_MODEL` - Model for prompt generation (default: deepseek-r1)
- `IMAGE_MODEL` - Model for image generation (default: gpt-image-1)
- `IMAGE_QUALITY` - Image quality (default: low)
- `IMAGE_SIZE` - Image size (default: 1024x1024)
- `IMAGE_MODERATION` - Image moderation level (default: low)
- `IMAGE_FORMAT` - Image format (default: png)

## Managing Illusion URLs

The bot can serve random illusions from a user-maintained collection. To add your own illusions:

1. Edit `data/illusion_urls.txt`
2. Add one image URL per line
3. Lines starting with `#` are treated as comments and ignored
4. Empty lines are ignored

Example format:
```txt
# Optical Illusion URLs
# Add one URL per line
https://example.com/illusion1.jpg
https://example.com/illusion2.jpg
```