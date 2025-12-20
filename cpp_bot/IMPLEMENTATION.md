# Optical Illusion Telegram Bot Implementation

## Overview
This document provides a comprehensive overview of the implementation of the optical illusion Telegram bot, which generates optical illusion images with two objects and asks users to determine which is larger.

## Architecture

The bot is implemented in C++ and consists of three main components:

1. **AIService** - Handles communication with AI APIs for generating prompts and images
2. **GameLogic** - Manages game state and challenges
3. **TelegramBot** - Main bot implementation that processes user commands and interactions

## Implementation Details

### AIService

The AIService class handles all communication with the AI APIs:

- **Prompt Generation**: Uses the `deepseek-v3.2` model to generate optical illusion prompts with two objects
- **Image Generation**: Uses the `gpt-image-1.5-low` model to generate images based on prompts
- **HTTP Client**: Reuses the existing boost::beast infrastructure for secure HTTP requests
- **Error Handling**: Implements robust error handling for network and API errors

### GameLogic

The GameLogic class manages the game state:

- **Challenge Management**: Tracks active challenges for users with timestamps
- **Answer Validation**: Validates user answers against correct answers
- **Timeout Handling**: Automatically cleans up expired challenges
- **Memory Management**: Efficiently stores and retrieves challenge data

### TelegramBot

The TelegramBot class has been enhanced with new functionality:

- **New Commands**: Added `/illusion` command for generating optical illusion challenges
- **Message Processing**: Extended to handle the new command while preserving existing functionality
- **Image Sending**: Added support for sending images via base64 data
- **Inline Buttons**: Implemented inline buttons for user responses
- **Callback Handling**: Added handler for button presses with immediate feedback

## Key Features

### Optical Illusion Generation
1. User sends `/illusion` command
2. Bot requests AI to generate a prompt for an optical illusion with two objects
3. Bot requests AI to generate an image based on the prompt
4. Bot stores the challenge with the correct answer
5. Bot sends the image to the user with three answer options as inline buttons

### User Interaction
1. User receives an image with three inline buttons: "First is larger", "Second is larger", "They are equal"
2. User selects one of the options
3. Bot validates the answer against the correct answer
4. Bot provides immediate feedback: "Correct! Well done." or "Incorrect. Try again!"

### Existing Functionality Preservation
- All existing commands (`/start`, `/help`, `/image_url`) continue to work
- No existing code paths were modified, only extended

## Technical Implementation

### Dependencies
- **Boost.Beast**: For HTTP client functionality and secure connections
- **nlohmann/json**: For JSON parsing and generation
- **OpenSSL**: For secure HTTPS connections

### Build System
- **CMake**: Used for building the project
- **C++20**: Required for modern C++ features
- **Modular Design**: Separate source files for each component

### Error Handling
- **Network Errors**: Robust handling of connection issues with appropriate user feedback
- **API Errors**: Proper parsing and handling of API error responses
- **Graceful Degradation**: Bot continues to function even when AI services are unavailable

## Usage

### Building
```bash
mkdir build
cd build
cmake ..
make
```

### Running
1. Set your Telegram bot token in `src/main.cpp`
2. Set your AI API key in `src/main.cpp`
3. Run the executable: `./telegram_bot`

### Commands
- `/start` - Welcome message and command list
- `/help` - Show available commands
- `/illusion` - Generate a new optical illusion challenge
- `/image_url` - Send a sample image (existing functionality)

## Future Improvements

1. **Configuration**: Load API keys from environment variables instead of hardcoding
2. **Database Storage**: Use a database for persistent challenge storage instead of in-memory storage
3. **Enhanced Error Handling**: More sophisticated retry mechanisms for transient failures
4. **Performance Optimization**: Connection pooling for HTTP requests
5. **Extended Features**: Multiple difficulty levels, scoring system, etc.

## Conclusion

The optical illusion Telegram bot has been successfully implemented with all required functionality. The implementation follows a modular architecture that separates concerns between AI service integration, game logic, and Telegram bot functionality. The bot preserves all existing functionality while adding the new optical illusion generation and user interaction features.