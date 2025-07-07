import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

from bot.stat_handler import router as stat_router
from bot.security_handler import AuthorizationMiddleware

# Инициализация бота
bot = Bot(
    token=os.getenv('TG_BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Роутеры и middleware
dp.include_router(stat_router)
dp.message.middleware(AuthorizationMiddleware())

# Стартовое сообщение
START_TEXT = (
    'Hi!'
    # '📊 <b>Привет! Добро пожаловать в бота статистики Wildberries!</b>'
    # '\n\n'
    # 'Я помогу тебе следить за динамикой заказов и продаж твоего магазина на Wildberries.'
    # '\n\n\n'
    # '🔍 <b>Что я умею:</b>'
    # '\n\n'
    # '📈 Показывать динамику заказов, продаж и отказов'
    # '\n\n'
    # '🔔 Присылать уведомления о новых заказах, выкупах и отказах'
    # '\n\n\n'
    # 'Выбери нужный раздел, чтобы получить данные. 🚀'
)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(START_TEXT)


async def create_bot_task():
    await dp.start_polling(bot)


# Вспомогательная функция для отправки сообщений извне
def send_message(chat_id: int, text: str, disable_notifications: bool = False, reply_markup=None):
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(
        bot.send_message(chat_id=chat_id, text=text, disable_notification=disable_notifications, reply_markup=reply_markup),
        loop
    )
