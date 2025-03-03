from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from api import wb_api, sheets_api

router = Router()


class Form(StatesGroup):
    waiting_for_url = State()


@router.message(Command('feedbacks'))
async def cmd_feedbacks(message: Message, state: FSMContext):
    await message.answer(f'Введи ссылку на товар')
    await state.set_state(Form.waiting_for_url)


@router.message(Form.waiting_for_url)
async def process_url(message: Message, state: FSMContext):
    nm = wb_api.get_item_id(message.text)
    if nm:
        await message.answer(f'Формирую отчет...')
        item = wb_api.load_details(nm)

        wb_api.load_feedbacks(item)
        wb_api.load_questions(item)
        spredsheet_id = sheets_api.fill_data(item)
        streadsheet_link = sheets_api.get_spreadsheet_link(spredsheet_id)

        await message.answer(f'Отчет сформирован:\n{streadsheet_link}')
    else:
        await message.answer(f'Товар не найден')
    await state.clear()