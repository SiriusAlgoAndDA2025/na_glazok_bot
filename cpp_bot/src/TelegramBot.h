#ifndef TELEGRAM_BOT_TELEGRAMBOT_H
#define TELEGRAM_BOT_TELEGRAMBOT_H

// library
#include <bits/stdc++.h>
#include <nlohmann/json.hpp>
#include <boost/beast.hpp>

// Include headers instead of forward declarations
#include "AIService.h"
#include "GameLogic.h"

using namespace std;

class TelegramBot {
public:
    TelegramBot(const string &token, const string &apiKey);

    void start();
private:
    string apiUrl, botToken, lastUpdateId;
    // apiUrl - в нее будем писать адрес телеграм апи + токен

    // botToken - в нее будем писать токен бота

    // lastUpdateId - используется для отслеживания последнего обработанного
    // обновления от Telegram API, для того, чтобы бот не обрабатывал одни
    // и те же обновления повторно.

    // AI service for generating prompts and images
    unique_ptr<AIService> aiService;
    
    // Game logic for managing challenges
    unique_ptr<GameLogic> gameLogic;

    void handleUpdates(const nlohmann::json& updates);
    void sendMessage(const string& chatId, const string &text);
    nlohmann::json makeRequest(const string& method, const nlohmann::json& payload = {});
    void sendPhotoByUrl(const string& chatId, const string& photoUrl, const string& caption = "");
    
    // New methods for optical illusion functionality
    void sendPhotoByData(const string& chatId, const string& base64Data, const string& caption = "");
    void sendIllusionChallenge(const string& chatId);
    void handleCallbackQuery(const nlohmann::json& callbackQuery);

    void processMessage(const string& chatId, const string &command);
};

#endif //TELEGRAM_BOT_TELEGRAMBOT_H
