#ifndef TELEGRAM_BOT_AISERVICE_H
#define TELEGRAM_BOT_AISERVICE_H

#include <string>
#include <nlohmann/json.hpp>
#include <vector>

// Forward declaration of log function
void log(const std::string& message);

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
    nlohmann::json makeRequest(const std::string& endpoint, const nlohmann::json& payload);
};

#endif // TELEGRAM_BOT_AISERVICE_H