#!/usr/bin/env python3
"""
Simple test script to verify the AIService functionality.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.telegram_bot.ai_service import AIService

# Load environment variables
load_dotenv()


async def main():
    """Main test function."""
    print('Testing AIService...')

    # Get API key from environment variable
    api_key = os.getenv('AI_API_KEY')
    if not api_key:
        print('Error: AI_API_KEY environment variable is not set')
        return 1

    ai_service = AIService(api_key)

    try:
        # Test prompt generation
        print('Generating prompt...')
        prompt_response = await ai_service.generate_prompt()
        print(f'Prompt: {prompt_response["prompt"]}')
        print(f'Correct Answer: {prompt_response["correctAnswer"]}')

        # Test image generation
        if prompt_response['prompt']:
            print('Generating image...')
            image_data = await ai_service.generate_image(prompt_response['prompt'])
            print(f'Image data length: {len(image_data)}')

            if image_data:
                print('Image generation successful!')
            else:
                print('Image generation failed - empty response')

        # Close the AI service
        await ai_service.close()

    except Exception as e:
        print(f'Error: {e}')
        return 1

    return 0


if __name__ == '__main__':
    asyncio.run(main())
