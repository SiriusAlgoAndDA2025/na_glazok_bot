#include "TelegramBot.h"
#include "bits/stdc++.h"

using namespace std;

int main() {
    // Try to get API keys from environment variables, fallback to hardcoded values for testing
    const string token = getenv("TELEGRAM_BOT_TOKEN") ? getenv("TELEGRAM_BOT_TOKEN") : "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const string apiKey = getenv("AI_API_KEY") ? getenv("AI_API_KEY") : "sk-aitunnel-...";
    
    if (token.empty()) {
        std::cerr << "Error: TELEGRAM_BOT_TOKEN environment variable is not set" << std::endl;
        return 1;
    }
    
    if (apiKey.empty()) {
        std::cerr << "Error: AI_API_KEY environment variable is not set" << std::endl;
        return 1;
    }
    
    // Warn if using hardcoded credentials
    if (getenv("TELEGRAM_BOT_TOKEN") == nullptr) {
        std::cout << "Warning: Using hardcoded Telegram bot token. For security, please set TELEGRAM_BOT_TOKEN environment variable." << std::endl;
    }
    
    if (getenv("AI_API_KEY") == nullptr) {
        std::cout << "Warning: Using hardcoded AI API key. For security, please set AI_API_KEY environment variable." << std::endl;
    }
    TelegramBot bot(token, apiKey);

    bot.start();
    return 0;
}