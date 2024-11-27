import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from services import sheets_api

from bot.feedbacks_handler import router as feedbacks_router

bot = Bot(token=os.getenv('TG_BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(feedbacks_router) 


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Hello, {message.from_user.first_name}!")


@dp.message(Command('help'))
async def cmd_help(message: Message):
    folder_link = sheets_api.get_folder_link(sheets_api.BOT_FOLDER_ID)

    result = "Список команд:\n"
    result += f"/feedbacks - формирование отчета по отзывам, вопросам/ответам.\n\nСсылка на папку со всеми отчетами: {folder_link}"
    await message.answer(result)


def run_bot():
    asyncio.run(dp.start_polling(bot))