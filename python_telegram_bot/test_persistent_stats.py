#!/usr/bin/env python3
"""
Test script for persistent statistics in the Optical Illusion Telegram Bot
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram_bot.game_logic import GameLogic


async def test_persistent_stats():
    """Test the persistent statistics functionality"""
    print('Testing persistent statistics functionality...')

    # Create a temporary data directory for testing
    test_data_dir = 'test_data'

    # Create GameLogic instance with test data directory
    game_logic = GameLogic(test_data_dir)

    # Test recording some answers
    print('Recording test answers...')
    game_logic.record_answer('test_user_1', True)
    game_logic.record_answer('test_user_1', False)
    game_logic.record_answer('test_user_1', True)
    game_logic.record_answer('test_user_2', False)

    # Check stats in memory
    stats1 = game_logic.get_user_stats('test_user_1')
    stats2 = game_logic.get_user_stats('test_user_2')

    print(f'User 1 stats: {stats1}')
    print(f'User 2 stats: {stats2}')

    # Verify stats
    assert stats1.total_challenges == 3
    assert stats1.correct_answers == 2
    assert stats2.total_challenges == 1
    assert stats2.correct_answers == 0

    # Create a new GameLogic instance to test loading from disk
    print('Testing loading from disk...')
    game_logic2 = GameLogic(test_data_dir)

    # Check that stats were loaded correctly
    loaded_stats1 = game_logic2.get_user_stats('test_user_1')
    loaded_stats2 = game_logic2.get_user_stats('test_user_2')

    print(f'Loaded User 1 stats: {loaded_stats1}')
    print(f'Loaded User 2 stats: {loaded_stats2}')

    # Verify loaded stats match saved stats
    assert loaded_stats1.total_challenges == stats1.total_challenges
    assert loaded_stats1.correct_answers == stats1.correct_answers
    assert loaded_stats2.total_challenges == stats2.total_challenges
    assert loaded_stats2.correct_answers == stats2.correct_answers

    # Clean up test data
    import shutil

    shutil.rmtree(test_data_dir)

    print('Persistent statistics test passed!')
    return True


async def main():
    """Main test function"""
    print('Running persistent statistics test for Optical Illusion Telegram Bot...')

    try:
        success = await test_persistent_stats()

        if success:
            print('Persistent statistics test passed!')
            sys.exit(0)
        else:
            print('Persistent statistics test failed!')
            sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())
