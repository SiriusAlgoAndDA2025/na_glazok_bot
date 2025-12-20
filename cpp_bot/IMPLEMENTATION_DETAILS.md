# Optical Illusion Telegram Bot - Implementation Details

## Overview
This document provides detailed information about the implementation of the Optical Illusion Telegram Bot. The bot generates optical illusion images with two objects and asks users to determine which is larger, integrating with AI services to create prompts and generate images.

## Architecture
The bot is implemented in C++ with a modular architecture consisting of three main components:

1. **AIService** - Handles communication with AI APIs
2. **GameLogic** - Manages game state and challenges
3. **TelegramBot** - Main bot implementation that processes user commands

## Key Features Implemented

### AI Service Integration
- Replaced Boost.Beast HTTP client with curl commands for API communication
- Implemented prompt generation using deepseek-r1 model
- Implemented image generation using gpt-image-1 model
- Added proper error handling and logging for API requests

### Game Logic
- Created Challenge structure to store optical illusion data
- Implemented user challenge tracking with timeout handling
- Added answer validation with immediate feedback

### Telegram Bot Enhancement
- Added new `/illusion` command for generating optical illusion challenges
- Implemented inline keyboard buttons for user responses
- Preserved existing `/image_url` functionality
- Added comprehensive logging throughout the application

## API Integration Details

### Prompt Generation
- Endpoint: `https://api.aitunnel.ru/v1/chat/completions`
- Model: `deepseek-r1`
- Prompt: "Create an optical illusion prompt with two objects where one appears larger than the other but they're actually the same size. Respond with the prompt for image generation and the correct answer (first/second/equal) in JSON format."

### Image Generation
- Endpoint: `https://api.aitunnel.ru/v1/images/generations`
- Model: `gpt-image-1`
- Parameters:
  - quality: medium
  - size: 1024x1024
  - moderation: low
  - output_format: png

## Implementation Notes

### curl Integration
All HTTP requests to AI services are now handled using curl commands executed via popen, which matches the behavior of the provided curl examples. This approach was chosen to:
1. Match the working examples provided in gpt.curl and imsge.curl
2. Simplify SSL handling by using curl's built-in certificate management
3. Reduce dependencies on Boost.Beast for HTTP communication

### Environment Variables
The bot now uses environment variables for API keys:
- `TELEGRAM_BOT_TOKEN` for Telegram bot token
- `AI_API_KEY` for AI service API key

This provides better security by avoiding hardcoded credentials in the source code.

Example:
```bash
export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'
export AI_API_KEY='your_ai_api_key_here'
```

### Error Handling
Comprehensive error handling has been implemented:
- API request failures are caught and logged
- JSON parsing errors are handled gracefully
- File I/O errors for temporary files are properly managed
- Network errors are caught and logged

## File Structure
```
src/
├── AIService.h/cpp       # AI service integration
├── GameLogic.h/cpp       # Game logic and challenge management
├── TelegramBot.h/cpp     # Telegram bot implementation
└── main.cpp             # Application entry point

CMakeLists.txt            # Build configuration
build_and_run.sh          # Build and run script
test_build.sh             # Test build script
README.md                 # Project documentation
test_plan.md              # Testing plan
IMPLEMENTATION_DETAILS.md  # This file
```

## Dependencies
- Boost.System (for networking utilities)
- nlohmann/json (for JSON parsing)
- OpenSSL (for secure connections)
- curl (for HTTP requests)

## Building and Running
The project can be built and run in several ways:

1. Using the build script:
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
   cmake .. -G "Unix Makefiles"
   make
   cd ..
   export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'
   export AI_API_KEY='your_ai_api_key_here'
   cmake-build-debug/telegram_bot

4. Quick start with default credentials:
   ```bash
   ./run_bot.sh
   ```
   ```

## Testing
A comprehensive test plan has been created in `test_plan.md` that covers:
- Basic bot functionality
- Optical illusion generation
- User response handling
- AI service integration
- Existing functionality preservation

## Future Improvements
1. Add unit tests for each component
2. Implement more sophisticated error recovery mechanisms
3. Add support for different types of optical illusions
4. Implement user statistics tracking
5. Add support for multiple languages