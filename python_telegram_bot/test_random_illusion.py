#!/usr/bin/env python3
"""
Test script for the random illusion functionality in the Optical Illusion Telegram Bot
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram_bot.bot import TelegramBot


async def test_random_illusion():
    """Test the random illusion functionality"""
    print('Testing random illusion functionality...')

    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    ai_api_key = os.getenv('AI_API_KEY')

    if not bot_token:
        print('Error: TELEGRAM_BOT_TOKEN not found in environment variables')
        return False

    if not ai_api_key:
        print('Error: AI_API_KEY not found in environment variables')
        return False

    # Create bot instance
    bot = TelegramBot(bot_token, ai_api_key)

    # Test getting random illusion URLs
    try:
        urls = bot._get_random_illusion_urls()
        print(f'Found {len(urls)} illusion URLs')

        if len(urls) > 0:
            print('Sample URLs:')
            for i, url in enumerate(urls[:3]):  # Show first 3 URLs
                print(f'  {i + 1}. {url}')
        else:
            print('No URLs found in illusion_urls.txt')

        print('Random illusion functionality test completed!')
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False


async def main():
    """Main test function"""
    print('Running random illusion test for Optical Illusion Telegram Bot...')

    success = await test_random_illusion()

    if success:
        print('Random illusion test passed!')
        sys.exit(0)
    else:
        print('Random illusion test failed!')
        sys.exit(1)


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())
