# GameLogic Design Document

## Overview
This document describes the design of the GameLogic class that will handle the optical illusion challenge game flow, including state management and answer validation.

## Class Interface

### GameLogic.h
```cpp
#ifndef TELEGRAM_BOT_GAMELOGIC_H
#define TELEGRAM_BOT_GAMELOGIC_H

#include <string>
#include <map>
#include <chrono>
#include <nlohmann/json.hpp>

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

## Method Details

### startChallenge()
This method will create a new challenge for a user and store it in the active challenges map.

**Parameters:**
- userId: Telegram user ID
- prompt: The prompt used to generate the image
- correctAnswer: The correct answer ("first", "second", or "equal")
- imageBase64: The base64 encoded image data

### checkAnswer()
This method will check if a user's answer is correct and remove the challenge from active challenges.

**Parameters:**
- userId: Telegram user ID
- userAnswer: The user's answer ("first", "second", or "equal")

**Returns:**
- true if the answer is correct, false otherwise

### getActiveChallenge()
This method will retrieve the active challenge for a user without removing it.

**Parameters:**
- userId: Telegram user ID

**Returns:**
- Pointer to the Challenge struct or nullptr if no active challenge

### cleanupExpiredChallenges()
This method will remove all expired challenges from the active challenges map.

## Data Structures

### Challenge
```cpp
struct Challenge {
    std::string userId;
    std::string prompt;
    std::string correctAnswer; // "first", "second", "equal"
    std::string imageBase64;
    std::chrono::time_point<std::chrono::system_clock> createdAt;
};
```

## Implementation Notes

### State Management
- Store active challenges in a std::map with userId as the key
- Clean up expired challenges periodically
- Thread safety considerations for concurrent access

### Timeout Handling
- Default timeout of 10 minutes for challenges
- Check for expired challenges when accessing them
- Automatic cleanup during challenge creation/checking

### Memory Management
- Store base64 image data directly in the challenge struct
- Consider memory usage for storing multiple images
- Potential optimization: store images in temporary files

## Dependencies
- Standard C++ libraries for data structures and time handling
- nlohmann/json for any JSON operations if needed