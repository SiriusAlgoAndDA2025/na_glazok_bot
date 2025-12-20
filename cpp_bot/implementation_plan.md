# Implementation Plan for Optical Illusion Telegram Bot

## Overview
This document provides a detailed implementation plan for adding optical illusion functionality to the existing Telegram bot. The implementation will be done in Code mode and will preserve all existing functionality.

## Components to Implement

### 1. AIService Class
Location: `src/AIService.h` and `src/AIService.cpp`

#### AIService.h
```cpp
#ifndef TELEGRAM_BOT_AISERVICE_H
#define TELEGRAM_BOT_AISERVICE_H

#include <string>
#include <nlohmann/json.hpp>
#include <vector>

struct PromptResponse {
    std::string prompt;
    std::string correctAnswer; // "first", "second", "equal"
};

class AIService {
public:
    AIService(const std::string& apiKey);
    
    // Generate an optical illusion prompt with two objects
    PromptResponse generatePrompt();
    
    // Generate an image based on a prompt
    std::string generateImage(const std::string& prompt);
    
private:
    std::string apiKey;
    std::string apiBaseUrl = "https://api.aitunnel.ru/v1";
    
    // Make HTTP POST request to AI API
    nlohmann::json makePostRequest(const std::string& endpoint, const nlohmann::json& payload);
    
    // Decode base64 image data
    std::vector<unsigned char> decodeBase64(const std::string& base64String);
};

#endif // TELEGRAM_BOT_AISERVICE_H
```

#### AIService.cpp
- Implementation of HTTP client using boost::beast (similar to existing TelegramBot.cpp)
- Implementation of generatePrompt() method calling `/chat/completions` endpoint
- Implementation of generateImage() method calling `/images/generations` endpoint
- Error handling for network and API errors
- Base64 decoding functionality

### 2. GameLogic Class
Location: `src/GameLogic.h` and `src/GameLogic.cpp`

#### GameLogic.h
```cpp
#ifndef TELEGRAM_BOT_GAMELOGIC_H
#define TELEGRAM_BOT_GAMELOGIC_H

#include <string>
#include <map>
#include <chrono>

struct Challenge {
    std::string userId;
    std::string prompt;
    std::string correctAnswer; // "first", "second", "equal"
    std::string imageBase64;
    std::chrono::time_point<std::chrono::system_clock> createdAt;
};

class GameLogic {
public:
    GameLogic();
    
    // Start a new challenge for a user
    void startChallenge(const std::string& userId, const std::string& prompt, 
                      const std::string& correctAnswer, const std::string& imageBase64);
    
    // Check a user's answer
    bool checkAnswer(const std::string& userId, const std::string& userAnswer);
    
    // Get active challenge for a user
    Challenge* getActiveChallenge(const std::string& userId);
    
    // Clean up expired challenges
    void cleanupExpiredChallenges();
    
private:
    std::map<std::string, Challenge> activeChallenges;
    std::chrono::minutes challengeTimeout = std::chrono::minutes(10);
    
    // Check if a challenge has expired
    bool isChallengeExpired(const Challenge& challenge);
};

#endif // TELEGRAM_BOT_GAMELOGIC_H
```

#### GameLogic.cpp
- Implementation of challenge management methods
- Timeout handling for challenges
- Memory management for active challenges

### 3. TelegramBot Enhancements
Location: `src/TelegramBot.h` and `src/TelegramBot.cpp`

#### Modifications to TelegramBot.h
- Add include for AIService and GameLogic
- Add member variables for AIService and GameLogic instances
- Add method for sending images with buttons

#### Modifications to TelegramBot.cpp
- Add new command handler for `/illusion`
- Preserve existing `/image_url` command functionality
- Add method for sending images with inline buttons
- Add handler for button callbacks
- Integrate with AIService and GameLogic

### 4. Main Application
Location: `src/main.cpp`

#### Modifications to main.cpp
- Add API key configuration (from environment variable only)
- Initialize AIService with API key
- Add validation for required environment variables

## Integration Points

### HTTP Client Reuse
- Reuse the existing HTTP client infrastructure from TelegramBot.cpp
- Extract common HTTP functionality into reusable methods
- Ensure SSL support for secure connections to AI APIs

### JSON Handling
- Use nlohmann::json for all JSON operations
- Parse AI API responses
- Generate request payloads

### Error Handling
- Network error handling with retries
- API error handling with user-friendly messages
- Graceful degradation when AI services are unavailable

## Build System
Location: `CMakeLists.txt`

### Modifications to CMakeLists.txt
- Add new source files to the build
- Ensure all dependencies are properly linked

## Environment Configuration
- API key should be configured via environment variable
- No hardcoded API keys in the source code

## Testing Strategy
1. Unit tests for AIService methods (with mocked HTTP responses)
2. Unit tests for GameLogic methods
3. Integration tests for the complete flow
4. Manual testing with actual AI services

## Deployment Considerations
- API key security (environment variables)
- Error handling for production use
- Logging for debugging and monitoring
- Performance considerations for concurrent users

## Implementation Order
1. AIService implementation
2. GameLogic implementation
3. TelegramBot enhancements
4. Main application updates
5. Build system updates
6. Testing and validation

## Backward Compatibility
- Preserve all existing commands and functionality
- Ensure existing code paths remain unchanged
- Add new functionality as extensions, not replacements