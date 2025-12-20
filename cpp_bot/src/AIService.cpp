#include "AIService.h"
#include <iostream>
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/beast.hpp>
#include <boost/beast/ssl.hpp>
#include <boost/archive/iterators/base64_from_binary.hpp>
#include <boost/archive/iterators/transform_width.hpp>
#include <boost/archive/iterators/ostream_iterator.hpp>
#include <openssl/ssl.h>
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <string>
#include <array>
#include <regex>

using tcp = boost::asio::ip::tcp;
namespace http = boost::beast::http;

nlohmann::json AIService::makeRequest(const std::string& endpoint, const nlohmann::json& payload) {
    try {
        log("[AIService] Making HTTP request to: " + endpoint);
        boost::asio::io_context ioc;

        // SSL Context
        boost::asio::ssl::context ssl_ctx(boost::asio::ssl::context::tlsv12_client);
        ssl_ctx.set_default_verify_paths();
        
        // Add certificate verification
        ssl_ctx.set_verify_mode(boost::asio::ssl::verify_peer);

        tcp::resolver resolver(ioc);
        boost::beast::ssl_stream<boost::beast::tcp_stream> stream(ioc, ssl_ctx);

        // Resolve host and connect
        auto const results = resolver.resolve("api.aitunnel.ru", "443");
        boost::beast::get_lowest_layer(stream).connect(results);

        // Perform SSL handshake
        log("[AIService] Performing SSL handshake with api.aitunnel.ru");
        stream.handshake(boost::asio::ssl::stream_base::client);

        // Create HTTP request
        http::request<http::string_body> req{http::verb::post, endpoint, 11};
        req.set(http::field::host, "api.aitunnel.ru");
        req.set(http::field::content_type, "application/json");
        req.set(http::field::authorization, "Bearer " + apiKey);
        req.body() = payload.dump();
        req.prepare_payload();
        
        log("[AIService] Sending HTTP request: " + endpoint);

        // Send the request
        http::write(stream, req);

        // Receive the response
        boost::beast::flat_buffer buffer;
        http::response<http::string_body> res;
        http::read(stream, buffer, res);
        
        log("[AIService] Received HTTP response, status: " + std::to_string(static_cast<int>(res.result())));

        // Shut down the SSL stream
        boost::system::error_code ec;
        stream.shutdown(ec);

        // Ignore the "stream truncated" error, as it is common during SSL shutdown
        if (ec == boost::asio::ssl::error::stream_truncated) {
            ec.assign(0, ec.category());
        } else if (ec) {
            log("[AIService] SSL shutdown error: " + ec.message());
            throw boost::system::system_error(ec);
        }

        // Parse and return the response body as JSON
        log("[AIService] Parsing response body, length: " + std::to_string(res.body().length()));
        if (res.body().length() > 0) {
            log("[AIService] Response body (first 500 chars): " + res.body().substr(0, std::min(500, (int)res.body().length())));
        }
        return nlohmann::json::parse(res.body());
    } catch (const std::exception& e) {
        log("[AIService] HTTP request failed: " + std::string(e.what()));
        throw std::runtime_error(std::string("Request failed: ") + e.what());
    }
}

AIService::AIService(const std::string& apiKey) : apiKey(apiKey) {}

PromptResponse AIService::generatePrompt() {
    log("[AIService] Generating prompt with deepseek-r1 using HTTP request");
    
    // Create JSON payload using nlohmann::json
    nlohmann::json payload;
    payload["model"] = "deepseek-r1";
    payload["max_tokens"] = 50000;
    
    nlohmann::json message;
    message["role"] = "user";
    message["content"] = "Create an optical illusion prompt with two objects where one appears larger than the other but they're actually the same size. Respond with the prompt for image generation and the correct answer (first/second/equal) in JSON format like this: {\"prompt\": \"prompt text\", \"correctAnswer\": \"first/second/equal\"}";
    
    payload["messages"] = nlohmann::json::array();
    payload["messages"].push_back(message);
    
    // Make HTTP request
    auto jsonResponse = makeRequest("/v1/chat/completions", payload);
    
    // Parse response
    PromptResponse result;
    try {
        if (jsonResponse.contains("choices") && jsonResponse["choices"].size() > 0) {
            std::string content = jsonResponse["choices"][0]["message"]["content"];
            log("[AIService] Received prompt response: " + content.substr(0, 100) + "...");
            // Parse the JSON content from the AI response
            try {
                // Try to parse the entire content as JSON first
                auto jsonContent = nlohmann::json::parse(content);
                result.prompt = jsonContent.value("prompt", "");
                result.correctAnswer = jsonContent.value("correctAnswer", "");
                // If correctAnswer is not found, try "answer"
                if (result.correctAnswer.empty()) {
                    result.correctAnswer = jsonContent.value("answer", "equal");
                }
            } catch (const std::exception& e) {
                // If parsing fails, try to extract JSON from code block
                log("[AIService] Warning: Failed to parse JSON, trying to extract from code block");
                try {
                    // Try to find JSON in code block
                    size_t start = content.find("{");
                    size_t end = content.rfind("}");
                    if (start != std::string::npos && end != std::string::npos && end > start) {
                        std::string jsonStr = content.substr(start, end - start + 1);
                        auto jsonContent = nlohmann::json::parse(jsonStr);
                        result.prompt = jsonContent.value("prompt", "");
                        result.correctAnswer = jsonContent.value("correctAnswer", "");
                        // If correctAnswer is not found, try "answer"
                        if (result.correctAnswer.empty()) {
                            result.correctAnswer = jsonContent.value("answer", "equal");
                        }
                        log("[AIService] Successfully extracted prompt and answer from code block");
                    } else {
                        // If no JSON found, try to find a JSON-like pattern
                        std::regex jsonPattern(R"(\{[^{}]*"prompt"[^{}]*"correctAnswer"[^{}]*\})");
                        std::smatch match;
                        if (std::regex_search(content, match, jsonPattern)) {
                            std::string jsonStr = match.str();
                            auto jsonContent = nlohmann::json::parse(jsonStr);
                            result.prompt = jsonContent.value("prompt", "");
                            result.correctAnswer = jsonContent.value("correctAnswer", "equal");
                            log("[AIService] Successfully extracted prompt and answer using regex");
                        } else {
                            // If no JSON found, use raw content
                            log("[AIService] No JSON found in response, using raw content");
                            result.prompt = content;
                            result.correctAnswer = "equal"; // Default answer
                        }
                    }
                } catch (const std::exception& e2) {
                    // If all parsing fails, use raw content
                    log("[AIService] Warning: Failed to parse JSON from code block, using raw content");
                    result.prompt = content;
                    result.correctAnswer = "equal"; // Default answer
                }
            }
        }
    } catch (const std::exception& e) {
        log("[AIService] Error parsing response: " + std::string(e.what()));
        throw;
    }
    
    return result;
}

std::string AIService::generateImage(const std::string& prompt) {
    log("[AIService] Generating image with gpt-image-1 using HTTP request");
    
    // Create JSON payload using nlohmann::json to properly escape special characters
    nlohmann::json payload;
    payload["model"] = "gpt-image-1";
    payload["prompt"] = prompt;
    payload["quality"] = "medium";
    payload["size"] = "1024x1536";
    payload["moderation"] = "low";
    payload["output_format"] = "png";
    
    // Make HTTP request
    auto jsonResponse = makeRequest("/v1/images/generations", payload);
    
    // Parse response
    try {
        if (jsonResponse.contains("data") && jsonResponse["data"].size() > 0) {
            std::string imageData = jsonResponse["data"][0].value("b64_json", "");
            log("[AIService] Received image data, length: " + std::to_string(imageData.length()));
            return imageData;
        }
    } catch (const std::exception& e) {
        log("[AIService] Error parsing image response: " + std::string(e.what()));
        throw;
    }
    
    log("[AIService] Warning: No image data received");
    throw std::runtime_error("No image data received from AI service");
}