#!/usr/bin/env python3
"""
Main entry point for the Optical Illusion Telegram Bot
"""

import asyncio
import os
import signal
import sys
from dotenv import load_dotenv
from telegram_bot.bot import TelegramBot

# Load environment variables
load_dotenv()


async def main():
    """Main function to run the bot"""
    # Get configuration from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    ai_api_key = os.getenv('AI_API_KEY')

    if not bot_token:
        print('Error: TELEGRAM_BOT_TOKEN not found in environment variables')
        print('Please set TELEGRAM_BOT_TOKEN in your .env file')
        sys.exit(1)

    if not ai_api_key:
        print('Error: AI_API_KEY not found in environment variables')
        print('Please set AI_API_KEY in your .env file')
        sys.exit(1)

    # Create and start bot
    bot = TelegramBot(bot_token, ai_api_key)

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f'Received signal {signum}')
        asyncio.create_task(bot.stop())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await bot.start()
    except KeyboardInterrupt:
        print('Received interrupt signal')
    except Exception as e:
        print(f'Error running bot: {e}')
    finally:
        try:
            await bot.stop()
        except RuntimeError:
            # Polling is not started, ignore
            pass
        except Exception as e:
            print(f'Error stopping bot: {e}')


if __name__ == '__main__':
    asyncio.run(main())
