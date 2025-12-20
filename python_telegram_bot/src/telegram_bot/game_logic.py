import logging
import os
import aiosqlite
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Challenge:
    """Represents an optical illusion challenge for a user."""

    user_id: str
    prompt: str
    correct_answer: str  # "left", "right", "equal"
    explanation: str  # Explanation of why the answer is correct
    image_base64: str
    created_at: datetime


@dataclass
class UserStats:
    """Represents user statistics."""

    total_challenges: int = 0
    correct_answers: int = 0
    username: str = ''  # Telegram username/nickname


class GameLogic:
    """Manages game state and challenges for the optical illusion bot."""

    def __init__(self, data_dir: str = 'data'):
        self.active_challenges: Dict[str, Challenge] = {}
        self.user_stats: Dict[str, UserStats] = {}
        self.challenge_timeout = timedelta(minutes=10)
        self.data_dir = data_dir
        self.db_file = os.path.join(data_dir, 'user_stats.db')

        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize the database and create tables if they don't exist"""
        try:
            # Create tables synchronously
            async def init_tables():
                await self._create_tables()

            # Try to get the running loop, if it exists
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, create a task
                loop.create_task(init_tables())
            except RuntimeError:
                # No running loop, create a new one
                loop = asyncio.new_event_loop()
                loop.run_until_complete(init_tables())
        except Exception as e:
            logger.error(f'[GameLogic] Error initializing database: {e}')

    async def _create_tables(self):
        """Create database tables"""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id TEXT PRIMARY KEY,
                    total_challenges INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    username TEXT DEFAULT ''
                )
            """)
            await db.commit()
            logger.info('[GameLogic] Database tables created/verified')

    async def _save_stats(self, user_id: str):
        """Save user statistics to database"""
        # Create a lock for database writes
        if not hasattr(self, '_db_lock'):
            self._db_lock = asyncio.Lock()

        try:
            async with self._db_lock:
                async with aiosqlite.connect(self.db_file) as db:
                    # Use INSERT OR REPLACE to handle both new and existing users
                    await db.execute(
                        """
                        INSERT OR REPLACE INTO user_stats (user_id, total_challenges, correct_answers, username)
                        VALUES (?, ?, ?, ?)
                    """,
                        (
                            user_id,
                            self.user_stats[user_id].total_challenges,
                            self.user_stats[user_id].correct_answers,
                            self.user_stats[user_id].username,
                        ),
                    )
                    await db.commit()
            logger.info(f'[GameLogic] Saved stats for user {user_id}')
        except Exception as e:
            logger.error(f'[GameLogic] Error saving stats for user {user_id}: {e}')

    def start_challenge(
        self,
        user_id: str,
        prompt: str,
        correct_answer: str,
        explanation: str,
        image_base64: str,
    ) -> None:
        """
        Start a new challenge for a user.

        Args:
            user_id: Telegram user ID
            prompt: The prompt used to generate the image
            correct_answer: The correct answer ("first", "second", or "equal")
            explanation: Explanation of why the answer is correct
            image_base64: The base64 encoded image data
        """
        logger.info(f'[GameLogic] Starting challenge for user {user_id}')

        challenge = Challenge(
            user_id=user_id,
            prompt=prompt,
            correct_answer=correct_answer,
            explanation=explanation,
            image_base64=image_base64,
            created_at=datetime.now(),
        )

        self.active_challenges[user_id] = challenge
        logger.info(f'[GameLogic] Challenge started for user {user_id} with answer: {correct_answer}')

    def check_answer(self, user_id: str, user_answer: str) -> bool:
        """
        Check a user's answer and remove the challenge.

        Args:
            user_id: Telegram user ID
            user_answer: The user's answer ("first", "second", or "equal")

        Returns:
            True if the answer is correct, False otherwise
        """
        logger.info(f'[GameLogic] Checking answer for user {user_id}: {user_answer}')

        if user_id in self.active_challenges:
            challenge = self.active_challenges[user_id]
            is_correct = challenge.correct_answer == user_answer
            logger.info(f'[GameLogic] User {user_id} answer is {"correct" if is_correct else "incorrect"}')

            # Record the answer for statistics
            self.record_answer(user_id, is_correct)

            # Remove the challenge after checking
            del self.active_challenges[user_id]
            return is_correct

        logger.info(f'[GameLogic] No active challenge found for user {user_id}')
        return False

    def record_answer(self, user_id: str, is_correct: bool) -> None:
        """
        Record a user's answer for statistics.

        Args:
            user_id: Telegram user ID
            is_correct: Whether the answer was correct
        """
        # Initialize user stats if not exists
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats()

        # Update stats
        self.user_stats[user_id].total_challenges += 1
        if is_correct:
            self.user_stats[user_id].correct_answers += 1

        logger.info(f'[GameLogic] Updated stats for user {user_id}: {self.user_stats[user_id]}')

        # Save stats to database
        async def save_stats_async():
            await self._save_stats(user_id)

        # Try to get the running loop, if it exists
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, create a task
            loop.create_task(save_stats_async())
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            loop.run_until_complete(save_stats_async())

    async def get_user_stats(self, user_id: str) -> UserStats:
        """
        Get user statistics.

        Args:
            user_id: Telegram user ID

        Returns:
            UserStats object
        """
        # First check if we have stats in memory
        if user_id in self.user_stats:
            return self.user_stats[user_id]

        # If not in memory, try to load from database
        try:
            async with aiosqlite.connect(self.db_file) as db:
                async with db.execute(
                    """
                    SELECT total_challenges, correct_answers, username
                    FROM user_stats
                    WHERE user_id = ?
                """,
                    (user_id,),
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        stats = UserStats(
                            total_challenges=row[0],
                            correct_answers=row[1],
                            username=row[2] if len(row) > 2 else '',
                        )
                        self.user_stats[user_id] = stats  # Cache in memory
                        return stats
        except Exception as e:
            logger.error(f'[GameLogic] Error loading stats for user {user_id}: {e}')

        # If no stats found, return default
        return UserStats()

    def get_active_challenge(self, user_id: str) -> Optional[Challenge]:
        """
        Get the active challenge for a user without removing it.

        Args:
            user_id: Telegram user ID

        Returns:
            Challenge object if active challenge exists, None otherwise
        """
        if user_id in self.active_challenges:
            challenge = self.active_challenges[user_id]
            if not self._is_challenge_expired(challenge):
                logger.info(f'[GameLogic] Found active challenge for user {user_id}')
                return challenge

        logger.info(f'[GameLogic] No active challenge found for user {user_id}')
        return None

    def cleanup_expired_challenges(self) -> None:
        """Clean up all expired challenges."""
        logger.info('[GameLogic] Cleaning up expired challenges')

        now = datetime.now()
        expired_users = []

        for user_id, challenge in self.active_challenges.items():
            if self._is_challenge_expired(challenge):
                logger.info(f'[GameLogic] Removing expired challenge for user {user_id}')
                expired_users.append(user_id)

        removed_count = 0
        for user_id in expired_users:
            del self.active_challenges[user_id]
            removed_count += 1

        logger.info(f'[GameLogic] Cleaned up {removed_count} expired challenges')

    def _is_challenge_expired(self, challenge: Challenge) -> bool:
        """
        Check if a challenge has expired.

        Args:
            challenge: The challenge to check

        Returns:
            True if the challenge has expired, False otherwise
        """
        now = datetime.now()
        duration = now - challenge.created_at
        expired = duration >= self.challenge_timeout

        if expired:
            logger.info(f'[GameLogic] Challenge expired, created {duration.total_seconds() / 60:.1f} minutes ago')

        return expired
