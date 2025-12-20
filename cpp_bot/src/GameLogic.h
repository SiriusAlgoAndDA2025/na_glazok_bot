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