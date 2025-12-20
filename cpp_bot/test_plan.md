# Test Plan for Optical Illusion Telegram Bot

## Overview
This document outlines the test plan for verifying the functionality of the Optical Illusion Telegram Bot. The bot generates optical illusion images with two objects and asks users to determine which is larger.

## Test Environment
- Telegram account with bot access
- Valid Telegram Bot API token
- Valid AI API key for aitunnel.ru
- Built executable of the telegram_bot application

## Test Cases

### 1. Basic Bot Functionality
**Objective:** Verify that the bot responds to basic commands.

**Steps:**
1. Start the bot application with valid API keys
2. Send `/start` command to the bot
3. Send `/help` command to the bot

**Expected Results:**
- Bot should respond with a welcome message for `/start`
- Bot should respond with a list of available commands for `/help`

### 2. Optical Illusion Generation
**Objective:** Verify that the bot can generate optical illusion challenges.

**Steps:**
1. Send `/illusion` command to the bot
2. Wait for the bot to generate a prompt and image
3. Verify that an image with buttons is received

**Expected Results:**
- Bot should generate a prompt using the AI service
- Bot should generate an image based on the prompt
- Bot should send the image with three answer buttons: "First is larger", "Second is larger", "They are equal"

### 3. User Response Handling
**Objective:** Verify that the bot correctly handles user responses.

**Steps:**
1. Send `/illusion` command to the bot
2. Click one of the answer buttons
3. Observe the bot's response

**Expected Results:**
- Bot should respond with feedback indicating whether the answer was correct or incorrect
- Bot should provide the correct answer if the user was incorrect

### 4. AI Service Integration
**Objective:** Verify that the bot correctly integrates with AI services.

**Steps:**
1. Check that the bot uses the correct models:
   - deepseek-r1 for prompt generation
   - gpt-image-1 for image generation
2. Verify that API requests are properly formatted
3. Check error handling for API failures

**Expected Results:**
- Bot should use the specified models for each AI service
- API requests should include proper headers and payload format
- Bot should handle API errors gracefully and provide meaningful error messages

### 5. Existing Functionality Preservation
**Objective:** Verify that existing functionality is preserved.

**Steps:**
1. Send `/image_url` command to the bot
2. Verify the response

**Expected Results:**
- Bot should respond with a sample image as before
- No existing functionality should be broken

## Test Execution

### Manual Testing
1. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN='your_telegram_bot_token_here'
   export AI_API_KEY='your_ai_api_key_here'
   ```

2. Run the bot:
   ```bash
   cd cmake-build-debug && ./telegram_bot
   ```

### Prerequisites Check
Before running the tests, ensure that:
- Both environment variables are set
- The build was successful
- The bot executable exists

3. Execute each test case and record results.

### Automated Testing
Currently, there are no automated tests implemented. Future improvements could include:
- Unit tests for AIService class
- Integration tests for GameLogic class
- End-to-end tests for TelegramBot class

## Success Criteria
- All test cases pass as expected
- Bot correctly generates optical illusions and handles user responses
- Existing functionality remains intact
- Error handling works properly for API failures