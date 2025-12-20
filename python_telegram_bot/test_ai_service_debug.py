#!/usr/bin/env python3
"""
Debug script for testing AIService functionality with detailed logging
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from src.telegram_bot.ai_service import AIService, PromptResponse

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    api_key = os.getenv('AI_API_KEY')
    base_url = os.getenv('AI_BASE_URL', 'https://api.aitunnel.ru')
    prompt_model = os.getenv('PROMPT_MODEL', 'deepseek-r1')

    if not api_key:
        print('Error: AI_API_KEY not found in environment variables')
        print('Please set AI_API_KEY in your .env file')
        return

    print('Testing AIService with detailed logging...')
    print(f'API Key: {api_key[:12]}...')
    print(f'Base URL: {base_url}')
    print(f'Prompt Model: {prompt_model}')
    print()

    try:
        # Create AIService instance
        async with AIService(api_key, base_url) as ai_service:
            # Test prompt generation
            print('Generating prompt...')
            prompt_response: PromptResponse = await ai_service.generate_prompt()
            print(f'Prompt: {prompt_response.prompt}')
            print(f'Correct Answer: {prompt_response.correct_answer}')
            print()

            # Test image generation (only if we have a prompt)
            if prompt_response.prompt:
                print('Generating image...')
                image_data = await ai_service.generate_image(prompt_response.prompt)
                print(f'Image data length: {len(image_data)}')
                print('Image generation successful!')
            else:
                print('No prompt generated, skipping image generation')

    except Exception as e:
        print(f'Error: {e}')
        logger.exception('Detailed error information:')


if __name__ == '__main__':
    asyncio.run(main())
