# AIService Design Document

## Overview
This document describes the design of the AIService class that will handle integration with the AI APIs for generating prompts and images for optical illusions.

## Class Interface

### AIService.h
```cpp
#ifndef TELEGRAM_BOT_AISERVICE_H
#define TELEGRAM_BOT_AISERVICE_H

#include <string>
#include <nlohmann/json.hpp>

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
};

#endif // TELEGRAM_BOT_AISERVICE_H
```

## Method Details

### generatePrompt()
This method will call the chat completions API to generate an optical illusion prompt.

**Request:**
- Endpoint: `/chat/completions`
- Model: `deepseek-v3.2`
- Prompt: "Create an optical illusion prompt with two objects where one appears larger than the other but they're actually the same size. Respond with the prompt for image generation and the correct answer (first/second/equal) in JSON format."

**Response:**
```json
{
  "prompt": "An image with two circles, one appearing larger due to surrounding context",
  "correctAnswer": "equal"
}
```

### generateImage()
This method will call the image generation API to create an image based on a prompt.

**Request:**
- Endpoint: `/images/generations`
- Model: `gpt-image-1.5-low`
- Parameters: quality="medium", size="1024x1024", moderation="low", output_format="png"

**Response:**
- Base64 encoded image data

## Implementation Notes

### HTTP Client
Reuse the existing HTTP client infrastructure from TelegramBot.cpp:
- boost::beast for HTTP requests
- SSL support for secure connections
- JSON parsing with nlohmann::json

### Error Handling
- Network errors should be caught and re-thrown as custom exceptions
- API errors should be parsed from JSON responses
- Retry mechanism for transient failures

### Configuration
- API key should be passed via constructor
- Base URL should be configurable
- Timeout values should be configurable

## Dependencies
- Boost.Beast (for HTTP requests)
- nlohmann/json (for JSON parsing)
- OpenSSL (for SSL support)