#include "GameLogic.h"
#include <chrono>
#include <iostream>

// Forward declaration of log function
void log(const std::string& message);

GameLogic::GameLogic() {}

void GameLogic::startChallenge(const std::string& userId, const std::string& prompt,
                              const std::string& correctAnswer, const std::string& imageBase64) {
    log("[GameLogic] Starting challenge for user " + userId);
    Challenge challenge;
    challenge.userId = userId;
    challenge.prompt = prompt;
    challenge.correctAnswer = correctAnswer;
    challenge.imageBase64 = imageBase64;
    challenge.createdAt = std::chrono::system_clock::now();
    
    activeChallenges[userId] = challenge;
    log("[GameLogic] Challenge started for user " + userId + " with answer: " + correctAnswer);
}

bool GameLogic::checkAnswer(const std::string& userId, const std::string& userAnswer) {
    log("[GameLogic] Checking answer for user " + userId + ": " + userAnswer);
    auto it = activeChallenges.find(userId);
    if (it != activeChallenges.end()) {
        bool isCorrect = (it->second.correctAnswer == userAnswer);
        log("[GameLogic] User " + userId + " answer is " + (isCorrect ? "correct" : "incorrect"));
        activeChallenges.erase(it);
        return isCorrect;
    }
    log("[GameLogic] No active challenge found for user " + userId);
    return false;
}

Challenge* GameLogic::getActiveChallenge(const std::string& userId) {
    auto it = activeChallenges.find(userId);
    if (it != activeChallenges.end() && !isChallengeExpired(it->second)) {
        log("[GameLogic] Found active challenge for user " + userId);
        return &it->second;
    }
    log("[GameLogic] No active challenge found for user " + userId);
    return nullptr;
}

void GameLogic::cleanupExpiredChallenges() {
    log("[GameLogic] Cleaning up expired challenges");
    auto now = std::chrono::system_clock::now();
    int removedCount = 0;
    for (auto it = activeChallenges.begin(); it != activeChallenges.end();) {
        if (isChallengeExpired(it->second)) {
            log("[GameLogic] Removing expired challenge for user " + it->first);
            it = activeChallenges.erase(it);
            removedCount++;
        } else {
            ++it;
        }
    }
    log("[GameLogic] Cleaned up " + std::to_string(removedCount) + " expired challenges");
}

bool GameLogic::isChallengeExpired(const Challenge& challenge) {
    auto now = std::chrono::system_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::minutes>(now - challenge.createdAt);
    bool expired = duration >= challengeTimeout;
    if (expired) {
        log("[GameLogic] Challenge expired, created " + std::to_string(duration.count()) + " minutes ago");
    }
    return expired;
}