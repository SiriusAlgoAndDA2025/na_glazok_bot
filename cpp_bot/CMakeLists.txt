cmake_minimum_required(VERSION 3.10)
project(telegram_bot)

set(CMAKE_CXX_STANDARD 20)

find_package(Boost REQUIRED COMPONENTS system)
find_package(nlohmann_json REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(CURL REQUIRED libcurl)

# Add src directory to include path
include_directories(src)
include_directories(${CURL_INCLUDE_DIRS})

add_executable(telegram_bot
        src/main.cpp
        src/TelegramBot.cpp
        src/TelegramBot.h
        src/AIService.cpp
        src/AIService.h
        src/GameLogic.cpp
        src/GameLogic.h)

add_executable(test_image_generation
        test_image_generation.cpp
        src/AIService.cpp
        src/AIService.h)

target_link_libraries(telegram_bot
        Boost::system
        OpenSSL::SSL
        OpenSSL::Crypto
        nlohmann_json::nlohmann_json
        ${CURL_LIBRARIES}

)

target_link_libraries(test_image_generation
        Boost::system
        OpenSSL::SSL
        OpenSSL::Crypto
        nlohmann_json::nlohmann_json
        ${CURL_LIBRARIES}

)

