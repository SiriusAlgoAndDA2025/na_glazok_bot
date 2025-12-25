import logging
import base64
import random
import pathlib
import typing
import aiogram
import aiogram.filters
import aiogram.types
from . import ai_service
from . import game_logic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, api_key: str):
        self.bot = aiogram.Bot(token=token)
        self.dp = aiogram.Dispatcher()
        self.ai_service = ai_service.AIService(api_key)
        self.game_logic = game_logic.GameLogic('data')
        self._illusion_urls_cache: typing.Optional[typing.List[typing.Tuple[str, str]]] = None

        # Register handlers
        self._register_handlers()

        logger.info(f'[TelegramBot] Initialized with token: {token[:10]}...')

    def _register_handlers(self):
        """Register command and message handlers"""
        self.dp.message(aiogram.filters.Command('start'))(self.handle_start)
        self.dp.message(aiogram.filters.Command('help'))(self.handle_help)
        self.dp.message(aiogram.filters.Command('illusion'))(self.handle_illusion)
        self.dp.message(aiogram.filters.Command('stats'))(self.handle_stats)
        self.dp.message(aiogram.filters.Command('leaderboard'))(self.handle_leaderboard)
        self.dp.message(aiogram.filters.Command('clear_x9k2m7p4w8n5q1r3v6z0j8h4g2f5d7s9a1c3e6b8'))(
            self.handle_reset_leaderboard
        )
        self.dp.message()(self.handle_message)  # Handle text messages for button presses
        self.dp.callback_query()(self.handle_callback_query)

    def _get_random_illusion_urls(self) -> typing.List[typing.Tuple[str, str]]:
        """Get all illusion URLs and descriptions from the file (cached in memory)."""
        if self._illusion_urls_cache is not None:
            return self._illusion_urls_cache

        illusions: typing.List[typing.Tuple[str, str]] = []
        try:
            data_file_path = pathlib.Path(__file__).resolve().parents[2] / 'data' / 'illusion_urls.txt'
            with data_file_path.open('r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Split URL and description if both are present
                        if '|' in line:
                            url, description = line.split('|', 1)
                            illusions.append((url.strip(), description.strip()))
                        else:
                            # No description provided
                            illusions.append((line, ''))
        except FileNotFoundError:
            logger.warning('[TelegramBot] illusion_urls.txt not found')
        except Exception as e:
            logger.error(f'[TelegramBot] Error reading illusion URLs: {e}')
        self._illusion_urls_cache = illusions
        return self._illusion_urls_cache

    def _create_main_menu(self) -> aiogram.types.ReplyKeyboardMarkup:
        """Create main menu keyboard with all commands"""
        keyboard = [
            [aiogram.types.KeyboardButton(text='🔮 Сгенерировать иллюзию')],
            [aiogram.types.KeyboardButton(text='🎲 Случайная иллюзия')],
            [aiogram.types.KeyboardButton(text='📊 Просмотр статистики')],
            [aiogram.types.KeyboardButton(text='🏆 Таблица лидеров')],
            [aiogram.types.KeyboardButton(text='ℹ️ Помощь')],
        ]
        return aiogram.types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

    async def handle_start(self, message: aiogram.types.Message):
        """Handle /start command"""
        logger.info(f'[TelegramBot] Received /start from user {message.from_user.id}')
        welcome_text = (
            'Добро пожаловать в бота оптических иллюзий! 👋\n\n'
            'Я генерирую увлекательные оптические иллюзии, которые поставят под сомнение ваше восприятие.\n\n'
            'Используйте меню ниже, чтобы начать:'
        )
        await message.answer(welcome_text, reply_markup=self._create_main_menu())

    async def handle_help(self, message: aiogram.types.Message):
        """Handle /help command"""
        logger.info(f'[TelegramBot] Received /help from user {message.from_user.id}')
        help_text = (
            'Помощь бота оптических иллюзий ℹ️\n\n'
            'Команды:\n'
            '🔮 Сгенерировать иллюзию - Создать новую задачу по оптической иллюзии\n'
            '🎲 Случайная иллюзия - Показать случайную иллюзию из коллекции\n'
            '📊 Просмотр статистики - Показать вашу статистику\n'
            '🏆 Таблица лидеров - Показать топ-10 участников\n'
            'ℹ️ Помощь - Показать это сообщение помощи\n\n'
            'Просто используйте кнопки ниже для навигации!'
        )
        await message.answer(help_text, reply_markup=self._create_main_menu())

    async def handle_message(self, message: aiogram.types.Message):
        """Handle text messages (button presses)"""
        logger.info(f'[TelegramBot] Received message from user {message.from_user.id}: {message.text}')

        # Handle button presses
        if message.text == '🔮 Сгенерировать иллюзию':
            # Call the illusion handler
            await self.handle_illusion(message)
        elif message.text == '🎲 Случайная иллюзия':
            # Handle random illusion request
            await self.handle_random_illusion(message)
        elif message.text == '📊 Просмотр статистики':
            # Call the stats handler
            await self.handle_stats(message)
        elif message.text == '🏆 Таблица лидеров':
            # Call the leaderboard handler
            await self.handle_leaderboard(message)
        elif message.text == 'ℹ️ Помощь':
            # Call the help handler
            await self.handle_help(message)
        else:
            # For any other message, show the menu
            await message.answer(
                'Please use the menu below to navigate:',
                reply_markup=self._create_main_menu(),
            )

    async def handle_random_illusion(self, message: aiogram.types.Message):
        """Handle random illusion request"""
        logger.info(f'[TelegramBot] Received random illusion request from user {message.from_user.id}')

        # Get random illusion URLs and descriptions
        illusions = self._get_random_illusion_urls()

        if not illusions:
            await message.answer(
                'Извините, в данный момент иллюзии недоступны. Пожалуйста, попробуйте позже.',
                reply_markup=self._create_main_menu(),
            )
            return

        # Select a random illusion
        random_illusion = random.choice(illusions)
        url, description = random_illusion

        # Create caption with description if available
        caption = 'Вот случайная оптическая иллюзия для вас! 🎲'
        if description:
            caption += f'\n\n{description}'

        try:
            # Send the image with description
            await self.bot.send_photo(
                chat_id=message.chat.id,
                photo=url,
                caption=caption,
                reply_markup=self._create_main_menu(),
                has_spoiler=False,
            )
        except Exception as e:
            logger.error(f'[TelegramBot] Error sending random illusion: {e}')
            await message.answer(
                'Извините, я не смог отправить иллюзию. Пожалуйста, попробуйте еще раз.',
                reply_markup=self._create_main_menu(),
            )

    async def handle_stats(self, message: aiogram.types.Message):
        """Handle /stats command"""
        user_id = str(message.from_user.id)
        logger.info(f'[TelegramBot] Received /stats from user {user_id}')

        # Get user stats
        stats = await self.game_logic.get_user_stats(user_id)

        # Create stats message
        if stats.total_challenges == 0:
            stats_text = (
                "Вы еще не завершили ни одной задачи. Используйте кнопку '🔮 Сгенерировать иллюзию', чтобы начать!"
            )
        else:
            accuracy = (stats.correct_answers / stats.total_challenges) * 100
            stats_text = (
                f'📊 Ваша статистика:\n'
                f'Всего задач: {stats.total_challenges}\n'
                f'Правильных ответов: {stats.correct_answers}\n'
                f'Точность: {accuracy:.1f}%'
            )

        await message.answer(stats_text, reply_markup=self._create_main_menu())

    async def handle_leaderboard(self, message: aiogram.types.Message):
        """Handle /leaderboard command"""
        user_id = str(message.from_user.id)
        logger.info(f'[TelegramBot] Received /leaderboard from user {user_id}')

        # Get leaderboard data
        leaderboard_data = await self.game_logic.get_leaderboard(user_id, limit=10)
        top_users = leaderboard_data['top_users']
        user_rank = leaderboard_data['user_rank']

        # Build leaderboard message
        if not top_users:
            leaderboard_text = 'Таблица лидеров пока пуста. Будьте первым, кто решит задачи! 🏆'
        else:
            leaderboard_text = '🏆 Таблица лидеров (Топ-10):\n\n'

            for rank, user_id_db, username, correct_answers, accuracy in top_users:
                # Use medal emojis for top 3
                if rank == 1:
                    prefix = '🥇'
                elif rank == 2:
                    prefix = '🥈'
                elif rank == 3:
                    prefix = '🥉'
                else:
                    prefix = f'{rank}.'

                leaderboard_text += f'{prefix} {username}: {correct_answers} правильных ({accuracy:.1f}%)\n'

            # Show user's position if not in top 10
            if user_rank:
                user_rank_num, _, user_username, user_correct, user_accuracy = user_rank
                if user_rank_num > 10:
                    leaderboard_text += '\n...\n'
                    leaderboard_text += (
                        f'{user_rank_num}. {user_username}: {user_correct} правильных ({user_accuracy:.1f}%) ← Вы\n'
                    )
                    leaderboard_text += '...\n'

        await message.answer(leaderboard_text, reply_markup=self._create_main_menu())

    async def handle_reset_leaderboard(self, message: aiogram.types.Message):
        """Handle secret command to reset leaderboard"""
        user_id = str(message.from_user.id)
        logger.warning(f'[TelegramBot] RESET LEADERBOARD requested by user {user_id}')

        try:
            # Reset the leaderboard
            await self.game_logic.reset_leaderboard()
            logger.warning('[TelegramBot] Leaderboard has been reset!')

            await message.answer(
                '🔄 Таблица лидеров успешно сброшена!\n\nВсе статистики удалены.',
                reply_markup=self._create_main_menu(),
            )
        except Exception as e:
            logger.error(f'[TelegramBot] Error resetting leaderboard: {e}')
            await message.answer(
                f'❌ Ошибка при сбросе таблицы лидеров: {str(e)}',
                reply_markup=self._create_main_menu(),
            )

    async def handle_illusion(self, message: aiogram.types.Message):
        """Handle /illusion command"""
        chat_id = str(message.chat.id)
        logger.info(f'[TelegramBot] Generating illusion challenge for chat {chat_id}')

        try:
            # Send initial message
            status_message = await message.answer('🧠 Генерация оптической иллюзии...')

            # Generate prompt
            logger.info('[TelegramBot] Requesting prompt generation from AI service')
            prompt_response = await self.ai_service.generate_prompt()
            logger.info(f'[TelegramBot] Received prompt: {prompt_response.prompt}')

            # Check if prompt is empty
            if not prompt_response.prompt:
                logger.warning('[TelegramBot] Warning: Empty prompt received from AI service')
                await status_message.edit_text(
                    'Извините, я не смог сгенерировать подходящий запрос для иллюзии. Пожалуйста, попробуйте еще раз.'
                )
                return

            # Update status message
            await status_message.edit_text('🎨 Создание изображения иллюзии...')

            # Generate image
            logger.info('[TelegramBot] Requesting image generation from AI service')
            base64_image = await self.ai_service.generate_image(prompt_response.prompt)
            logger.info(f'[TelegramBot] Finished image generation, received image data, length: {len(base64_image)}')

            if not base64_image:
                logger.warning('[TelegramBot] Warning: Empty image data received')
                await status_message.edit_text(
                    'Извините, я не смог сгенерировать изображение иллюзии. Пожалуйста, попробуйте еще раз.'
                )
                return

            # Update status message
            await status_message.edit_text('✅ Отправка иллюзии...')

            # Store challenge - use chat_id as key to match C++ implementation
            logger.info(f'[TelegramBot] Storing challenge with correct answer: {prompt_response.correct_answer}')
            self.game_logic.start_challenge(
                chat_id,
                prompt_response.prompt,
                prompt_response.correct_answer,
                prompt_response.explanation,
                base64_image,
            )
            logger.info('[TelegramBot] Finished storing challenge')

            # Create inline keyboard with options
            keyboard = aiogram.types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [aiogram.types.InlineKeyboardButton(text='Левый больше', callback_data='left')],
                    [aiogram.types.InlineKeyboardButton(text='Правый больше', callback_data='right')],
                    [aiogram.types.InlineKeyboardButton(text='Они равны', callback_data='equal')],
                ]
            )

            # Send image with buttons
            logger.info('[TelegramBot] Sending illusion challenge with buttons')
            # Convert base64 to InputFile
            image_bytes = base64.b64decode(base64_image)
            image_file = aiogram.types.BufferedInputFile(image_bytes, filename='illusion.png')

            # Caption asks user to guess what the AI thinks
            caption = '🤖 Какой объект, по мнению нейросети, кажется больше?'

            await self.bot.send_photo(
                chat_id=message.chat.id,
                photo=image_file,
                caption=caption,
                reply_markup=keyboard,
            )

            # Delete status message
            await status_message.delete()
            logger.info('[TelegramBot] Finished sending illusion challenge with buttons')

            # Send a message with the main menu
            await self.bot.send_message(
                chat_id=message.chat.id,
                text='Используйте меню ниже для дополнительных опций:',
                reply_markup=self._create_main_menu(),
            )

        except Exception as e:
            logger.error(f'[TelegramBot] Error generating illusion: {str(e)}')
            await message.answer(
                f'Извините, при генерации иллюзии произошла ошибка: {str(e)}. Пожалуйста, попробуйте еще раз.'
            )

    async def handle_callback_query(self, callback_query: aiogram.types.CallbackQuery):
        """Handle callback queries (button presses)"""
        chat_id = str(callback_query.message.chat.id)
        user_id = str(callback_query.from_user.id)
        callback_data = callback_query.data

        logger.info(f'[TelegramBot] Received callback from user {user_id}: {callback_data}')

        # Get username or first name for display
        username = callback_query.from_user.username or callback_query.from_user.first_name or 'Anonymous'

        # Answer the callback query to remove the loading indicator
        await callback_query.answer()

        # Check if there's an active challenge - use chat_id as key to match C++ implementation
        challenge = self.game_logic.get_active_challenge(chat_id)

        if challenge is None:
            # No active challenge, send message and return
            await callback_query.message.edit_reply_markup(reply_markup=None)
            await self.bot.send_message(chat_id, 'Эта задача уже была решена или истекло время.')
            return

        # Check the answer (only validates, doesn't record stats)
        # Use chat_id for challenge lookup
        is_correct = self.game_logic.check_answer(chat_id, callback_data)

        # Record the answer for user statistics with username
        # Use user_id for stats (not chat_id) to track individual users
        self.game_logic.record_answer(user_id, is_correct, username)

        # Remove the buttons from the message
        await callback_query.message.edit_reply_markup(reply_markup=None)

        # Send feedback
        if is_correct:
            logger.info(f'[TelegramBot] User {user_id} answered correctly')
            feedback_text = '✅ Правильно! Вы угадали мнение нейросети!'
            # Add correct answer and explanation if available
            if challenge.correct_answer and challenge.explanation:
                feedback_text += f'\n\n🤖 Ответ нейросети: {challenge.correct_answer}\n💡 Объяснение от нейросети: {challenge.explanation}'
            await self.bot.send_message(chat_id, feedback_text)
        else:
            logger.info(f'[TelegramBot] User {user_id} answered incorrectly')
            feedback_text = '❌ Неправильно. Нейросеть думает иначе!'
            # Add correct answer and explanation if available
            if challenge.correct_answer and challenge.explanation:
                feedback_text += f'\n\n🤖 Ответ нейросети: {challenge.correct_answer}\n💡 Объяснение от нейросети: {challenge.explanation}'
            await self.bot.send_message(chat_id, feedback_text)

        # Show the main menu after providing feedback
        await self.bot.send_message(
            chat_id=chat_id,
            text='Используйте меню ниже для дополнительных опций:',
            reply_markup=self._create_main_menu(),
        )

    async def start(self):
        """Start the bot"""
        logger.info('[TelegramBot] Starting Telegram bot...')
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f'[TelegramBot] Bot error: {str(e)}')
        finally:
            logger.info('[TelegramBot] Shutting down bot...')
            await self.ai_service.close()

    async def stop(self):
        """Stop the bot"""
        logger.info('[TelegramBot] Stopping bot...')
        await self.dp.stop_polling()
        await self.ai_service.close()
