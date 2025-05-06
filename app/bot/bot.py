import os
import asyncio

from aiogram import Bot, Dispatcher, flags
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

# from ...old.feedbacks_handler import router as feedbacks_router
from bot.stat_handler import router as stat_router
from bot.security_handler import AuthorizationMiddleware

bot = Bot(token=os.getenv('TG_BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# dp.include_router(feedbacks_router) 
dp.include_router(stat_router)
dp.message.middleware(AuthorizationMiddleware())

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


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


def start_bot():
    loop.create_task(dp.start_polling(bot))
    loop.run_forever()


def send_message(chat_id: int, text: str, disable_notifications: bool = False):
    asyncio.run_coroutine_threadsafe(bot.send_message(chat_id=chat_id, text=text, disable_notification=disable_notifications), loop)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(START_TEXT)
