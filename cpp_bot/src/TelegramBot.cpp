#include "TelegramBot.h"
#include "AIService.h"
#include "GameLogic.h"
#include <iostream>
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/beast.hpp>
#include <boost/beast/ssl.hpp>
#include <chrono>
#include <iomanip>
#include <sstream>

using tcp = boost::asio::ip::tcp;
namespace http = boost::beast::http;

// Simple logging function
void log(const std::string& message) {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
    ss << "." << std::setfill('0') << std::setw(3) << ms.count();
    std::cout << "[" << ss.str() << "] " << message << std::endl;
}

TelegramBot::TelegramBot(const std::string& token, const std::string& apiKey)
        : botToken(token), apiUrl("https://api.telegram.org/bot" + token) {
    aiService = std::make_unique<AIService>(apiKey);
    gameLogic = std::make_unique<GameLogic>();
    log("TelegramBot initialized with token: " + token.substr(0, 10) + "...");
}

void TelegramBot::start() {
    log("Starting Telegram bot...");
    int updateCount = 0;
    while (true) {
        try {
            // Get updates
            nlohmann::json payload;
            if (!lastUpdateId.empty()) {
                payload["offset"] = std::stoi(lastUpdateId) + 1;
            }
            auto response = makeRequest("getUpdates", payload);
            handleUpdates(response["result"]);
            
            // Periodically clean up expired challenges
            updateCount++;
            if (updateCount % 10 == 0) {  // Clean up every 10 update cycles
                gameLogic->cleanupExpiredChallenges();
            }
        } catch (const std::exception& e) {
            log("Error in main loop: " + std::string(e.what()));
            // Continue running even if there's an error
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }
}


void TelegramBot::handleUpdates(const nlohmann::json& updates) {
    for (const auto& update : updates) {
        if (update.contains("update_id")) {
            lastUpdateId = std::to_string(update["update_id"].get<int>());
        }
        
        // Handle messages
        if (update.contains("message") && update["message"].contains("text")) {
            std::string chatId = std::to_string(update["message"]["chat"]["id"].get<int>());
            std::string text = update["message"]["text"].get<std::string>();
            std::string userId = std::to_string(update["message"]["from"]["id"].get<int>());
            log("Received message from user " + userId + ": " + text);
            processMessage(chatId, text);
        }
        
        // Handle callback queries (button presses)
        if (update.contains("callback_query")) {
            handleCallbackQuery(update["callback_query"]);
        }
    }
}

void TelegramBot::sendMessage(const std::string& chatId, const std::string& text) {
    log("Sending message to chat " + chatId + ": " + text.substr(0, 50) + "...");
    nlohmann::json payload;
    payload["chat_id"] = chatId;
    payload["text"] = text;
    makeRequest("sendMessage", payload);
}

void TelegramBot::sendPhotoByUrl(const std::string& chatId, const std::string& photoUrl, const std::string& caption) {
    log("Sending photo by URL to chat " + chatId);
    nlohmann::json payload;
    payload["chat_id"] = chatId;
    payload["photo"] = photoUrl;
    if (!caption.empty()) {
        payload["caption"] = caption;
    }
    makeRequest("sendPhoto", payload);
}

void TelegramBot::sendPhotoByData(const std::string& chatId, const std::string& base64Data, const std::string& caption) {
    log("Sending photo by data to chat " + chatId);
    // For base64 data, we need to send it as a file upload
    // We'll use the photo parameter with the base64 data directly
    nlohmann::json payload;
    payload["chat_id"] = chatId;
    payload["photo"] = "data:image/png;base64," + base64Data;
    if (!caption.empty()) {
        payload["caption"] = caption;
    }
    makeRequest("sendPhoto", payload);
}

void TelegramBot::sendIllusionChallenge(const std::string& chatId) {
    log("Generating illusion challenge for chat " + chatId);
    try {
        // Generate prompt
        log("Requesting prompt generation from AI service");
        PromptResponse promptResponse = aiService->generatePrompt();
        log("Received prompt: " + promptResponse.prompt);
        
        // Check if prompt is empty
        if (promptResponse.prompt.empty()) {
            log("Warning: Empty prompt received from AI service");
            sendMessage(chatId, "Sorry, I couldn't generate a proper prompt for the illusion. Please try again.");
            return;
        }
        
        // Generate image
        log("Requesting image generation from AI service");
        std::string base64Image = aiService->generateImage(promptResponse.prompt);
        log("Finished image generation, received image data, length: " + std::to_string(base64Image.length()));
        
        if (base64Image.empty()) {
            log("Warning: Empty image data received");
            sendMessage(chatId, "Sorry, I couldn't generate the illusion image. Please try again.");
            return;
        }
        
        // Store challenge
        log("Storing challenge with correct answer: " + promptResponse.correctAnswer);
        gameLogic->startChallenge(chatId, promptResponse.prompt, promptResponse.correctAnswer, base64Image);
        log("Finished storing challenge");
        
        // Create inline keyboard with options
        nlohmann::json keyboard;
        keyboard["inline_keyboard"] = nlohmann::json::array();
        
        nlohmann::json row1 = nlohmann::json::array();
        nlohmann::json button1;
        button1["text"] = "First is larger";
        button1["callback_data"] = "first";
        row1.push_back(button1);
        
        nlohmann::json row2 = nlohmann::json::array();
        nlohmann::json button2;
        button2["text"] = "Second is larger";
        button2["callback_data"] = "second";
        row2.push_back(button2);
        
        nlohmann::json row3 = nlohmann::json::array();
        nlohmann::json button3;
        button3["text"] = "They are equal";
        button3["callback_data"] = "equal";
        row3.push_back(button3);
        
        keyboard["inline_keyboard"].push_back(row1);
        keyboard["inline_keyboard"].push_back(row2);
        keyboard["inline_keyboard"].push_back(row3);
        
        // Send image with buttons
        nlohmann::json payload;
        payload["chat_id"] = chatId;
        payload["photo"] = "data:image/png;base64," + base64Image;
        payload["caption"] = "Which object appears larger?";
        payload["reply_markup"] = keyboard;
        
        log("Sending illusion challenge with buttons");
        makeRequest("sendPhoto", payload);
        log("Finished sending illusion challenge with buttons");
    } catch (const std::exception& e) {
        log("Error generating illusion: " + std::string(e.what()));
        sendMessage(chatId, "Sorry, I encountered an error while generating the illusion: " + std::string(e.what()) + ". Please try again.");
    }
}

void TelegramBot::handleCallbackQuery(const nlohmann::json& callbackQuery) {
    std::string chatId = std::to_string(callbackQuery["message"]["chat"]["id"].get<int>());
    std::string userId = std::to_string(callbackQuery["from"]["id"].get<int>());
    std::string callbackData = callbackQuery["data"].get<std::string>();
    std::string callbackId = callbackQuery["id"].get<std::string>();
    
    log("Received callback from user " + userId + ": " + callbackData);
    
    // Answer the callback query to remove the loading indicator
    nlohmann::json answerPayload;
    answerPayload["callback_query_id"] = callbackId;
    makeRequest("answerCallbackQuery", answerPayload);
    
    // Check the answer
    bool isCorrect = gameLogic->checkAnswer(userId, callbackData);
    
    // Send feedback
    if (isCorrect) {
        log("User " + userId + " answered correctly");
        sendMessage(chatId, "Correct! Well done.");
    } else {
        log("User " + userId + " answered incorrectly");
        sendMessage(chatId, "Incorrect. Try again!");
    }
}

void TelegramBot::processMessage(const string& chatId, const string& text) {
    log("Processing command: " + text);

    if (text == "/start") {
        log("Sending welcome message");
        sendMessage(chatId, "Welcome! Available commands:\n/illusion - Generate an optical illusion\n/help - Show help");
    }
    else if (text == "/help") {
        log("Sending help message");
        sendMessage(chatId, "Available commands:\n/illusion - Generate an optical illusion\n/image_url - Send a sample image");
    } else if (text == "/illusion") {
        log("Generating illusion challenge");
        sendIllusionChallenge(chatId);
    } else if (text == "/image_url") {
        log("Sending sample image");
        // Пример с URL изображения (замените на реальный URL)
        sendPhotoByUrl(chatId,
                       "https://vk.com/wall-186827059_25467",
                       "");
    } else {
        log("Unknown command: " + text);
        sendMessage(chatId, "Unknown command. Type /help for available commands.");
    }
}

nlohmann::json TelegramBot::makeRequest(const std::string& method, const nlohmann::json& payload) {
    try {
        log("Making HTTP request to: " + method);
        boost::asio::io_context ioc;

        // SSL Context
        boost::asio::ssl::context ssl_ctx(boost::asio::ssl::context::tlsv12_client);
        ssl_ctx.set_default_verify_paths();
        
        // Add certificate verification
        ssl_ctx.set_verify_mode(boost::asio::ssl::verify_peer);

        tcp::resolver resolver(ioc);
        boost::beast::ssl_stream<boost::beast::tcp_stream> stream(ioc, ssl_ctx);

        // Resolve host and connect
        auto const results = resolver.resolve("api.telegram.org", "443");
        boost::beast::get_lowest_layer(stream).connect(results);

        // Perform SSL handshake
        log("Performing SSL handshake with api.telegram.org");
        stream.handshake(boost::asio::ssl::stream_base::client);

        // Create HTTP request
        http::request<http::string_body> req{http::verb::post, "/bot" + botToken + "/" + method, 11};
        req.set(http::field::host, "api.telegram.org");
        req.set(http::field::content_type, "application/json");
        req.body() = payload.dump();
        req.prepare_payload();
        
        log("Sending HTTP request: " + method);

        // Send the request
        http::write(stream, req);

        // Receive the response
        boost::beast::flat_buffer buffer;
        http::response<http::string_body> res;
        http::read(stream, buffer, res);
        
        log("Received HTTP response, status: " + std::to_string(static_cast<int>(res.result())));

        // Shut down the SSL stream
        boost::system::error_code ec;
        stream.shutdown(ec);

        // Ignore the "stream truncated" error, as it is common during SSL shutdown
        if (ec == boost::asio::ssl::error::stream_truncated) {
            ec.assign(0, ec.category());
        } else if (ec) {
            log("SSL shutdown error: " + ec.message());
            throw boost::system::system_error(ec);
        }

        // Parse and return the response body as JSON
        log("Parsing response body, length: " + std::to_string(res.body().length()));
        if (res.body().length() > 0) {
            log("Response body (first 500 chars): " + res.body().substr(0, std::min(500, (int)res.body().length())));
        }
        return nlohmann::json::parse(res.body());
    } catch (const std::exception& e) {
        log("HTTP request failed: " + std::string(e.what()));
        throw std::runtime_error(std::string("Request failed: ") + e.what());
    }
}

