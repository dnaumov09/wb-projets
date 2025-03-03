import os
import asyncio

from aiogram import Bot, Dispatcher, flags
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from bot.feedbacks_handler import router as feedbacks_router
from bot.stat_handler import router as stat_router
from bot.security_handler import AuthorizationMiddleware

bot = Bot(token=os.getenv('TG_BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(feedbacks_router) 
dp.include_router(stat_router)
dp.message.middleware(AuthorizationMiddleware())

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def start_bot():
    loop.create_task(dp.start_polling(bot))
    loop.run_forever()


def send_message(chat_id: int, text: str):
    asyncio.run_coroutine_threadsafe(bot.send_message(chat_id=chat_id, text=text), loop)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"OK")
