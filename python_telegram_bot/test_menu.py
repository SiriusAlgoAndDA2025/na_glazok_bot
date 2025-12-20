#!/usr/bin/env python3
"""
Test script for the Optical Illusion Telegram Bot Menu
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram_bot.bot import TelegramBot


async def test_menu():
    """Test the menu functionality"""
    print('Testing menu functionality...')

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

    # Test the main menu creation
    try:
        menu = bot._create_main_menu()
        print('Main menu created successfully!')
        print(f'Menu has {len(menu.keyboard)} rows')
        for i, row in enumerate(menu.keyboard):
            print(f'Row {i + 1}: {len(row)} buttons')
            for j, button in enumerate(row):
                print(f'  Button {j + 1}: {button.text}')

        print('Menu test passed!')
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False


async def main():
    """Main test function"""
    print('Running menu test for Optical Illusion Telegram Bot...')

    success = await test_menu()

    if success:
        print('Menu test passed!')
        sys.exit(0)
    else:
        print('Menu test failed!')
        sys.exit(1)


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())
