#include "AIService.h"
#include <iostream>
#include <string>

// Mock log function
void log(const std::string& message) {
    std::cout << message << std::endl;
}

int main() {
    // Replace with your actual API key
    const char* apiKeyEnv = getenv("AI_API_KEY");
    std::string apiKey = apiKeyEnv ? apiKeyEnv : "sk-aitunnel-...";
    
    if (apiKeyEnv == nullptr) {
        std::cout << "Warning: Using hardcoded AI API key. For security, please set AI_API_KEY environment variable." << std::endl;
    }
    
    AIService aiService(apiKey);
    
    try {
        // Test prompt generation
        std::cout << "Generating prompt..." << std::endl;
        PromptResponse promptResponse = aiService.generatePrompt();
        std::cout << "Prompt: " << promptResponse.prompt << std::endl;
        std::cout << "Correct Answer: " << promptResponse.correctAnswer << std::endl;
        
        // Test image generation
        if (!promptResponse.prompt.empty()) {
            std::cout << "Generating image..." << std::endl;
            std::string imageData = aiService.generateImage(promptResponse.prompt);
            std::cout << "Image data length: " << imageData.length() << std::endl;
            
            if (!imageData.empty()) {
                std::cout << "Image generation successful!" << std::endl;
            } else {
                std::cout << "Image generation failed - empty response" << std::endl;
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}