#!/usr/bin/env python3
"""
Test script for the Optical Illusion Telegram Bot
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from src.telegram_bot.ai_service import AIService, PromptResponse
from src.telegram_bot.game_logic import GameLogic


async def test_ai_service():
    """Test AIService functionality"""
    print('Testing AIService...')

    try:
        # Create AIService instance
        api_key = os.getenv('AI_API_KEY')
        base_url = os.getenv('AI_BASE_URL', 'https://api.aitunnel.ru/v1')

        if not api_key:
            print('Error: AI_API_KEY not found in environment variables')
            return False

        async with AIService(api_key, base_url) as ai_service:
            # Test prompt generation
            print('Generating prompt...')
            prompt_response: PromptResponse = await ai_service.generate_prompt()
            print(f'Prompt: {prompt_response.prompt[:100]}...')
            print(f'Correct Answer: {prompt_response.correct_answer}')

            # Test image generation (only if we have a prompt)
            if prompt_response.prompt:
                print('Generating image...')
                image_data = await ai_service.generate_image(prompt_response.prompt)
                print(f'Image data length: {len(image_data)}')
                print('AIService test passed!')
                return True
            else:
                print('No prompt generated')
                return False

    except Exception as e:
        print(f'Error: {e}')
        return False


def test_game_logic():
    """Test GameLogic functionality"""
    print('Testing GameLogic...')

    try:
        # Create GameLogic instance
        game_logic = GameLogic()

        # Test starting a challenge
        chat_id = 'test_chat'
        prompt = 'Test prompt'
        correct_answer = 'first'
        image_data = 'test_image_data'

        game_logic.start_challenge(chat_id, prompt, correct_answer, image_data)

        # Test checking answer
        is_correct = game_logic.check_answer(chat_id, 'first')
        print(f'Correct answer check: {is_correct}')

        # Start another challenge for incorrect answer test
        game_logic.start_challenge(chat_id, prompt, correct_answer, image_data)
        is_incorrect = game_logic.check_answer(chat_id, 'second')
        print(f'Incorrect answer check: {is_incorrect}')

        print('GameLogic test passed!')
        return True

    except Exception as e:
        print(f'Error: {e}')
        return False


async def main():
    """Main test function"""
    print('Running tests for Optical Illusion Telegram Bot...')

    # Load environment variables
    load_dotenv()

    # Run tests
    ai_success = await test_ai_service()
    game_success = test_game_logic()

    if ai_success and game_success:
        print('All tests passed!')
        sys.exit(0)
    else:
        print('Some tests failed!')
        sys.exit(1)


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())
