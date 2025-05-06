from aiogram import Router
from aiogram.filters import Command
from datetime import timedelta
import locale

from aiogram.types import Message
# from db.functions import get_pipeline_statistics, get_date_ranges

router = Router()

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
RU_WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
RU_MONTHS = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]


@router.message(Command('ping'))
async def cmd_pipeline(message: Message):
    await message.answer('OK')


# @router.message(Command('pipeline'))
# async def cmd_pipeline(message: Message):
#     await message.answer((
#         '📈 <b>Динамика продаж</b>'
#         '\n\n' + build_pipeline_data()
#     ))
    


def build_pipeline_data() -> str:
    # date_ranges = get_date_ranges()
    # pipeline_stats = get_pipeline_statistics(is_aggregated=True)
    
    # result = ''
    # for period_name, data in pipeline_stats.items():
    #     header = format_period_name(period_name, date_ranges)
    #     result += f"<b>{header}</b>\n"
    #     result += (format_stat_data(period_name, data[0]) if data else '---\n') + '\n'
    
    # return result
    return ''

#fro detailed
# for row in data:
    # format_stat_data(period_name, data)


def format_stat_data(period: str, stat) -> str:
    oreders_count = stat['orders_count']
    sales_count = stat['sales_count']
    cancel_count = stat['orders_cancelled_count'] if stat['orders_cancelled_count'] else 0
    return_count = stat['sales_returned_count'] if stat['sales_returned_count'] else 0

    result = ""
    result += f"Заказов: <b>{oreders_count}</b>"
    result += f" ({format(round(stat['orders_sum']), ",d").replace(",", " ")} руб.)\n" if oreders_count > 0 else "\n"
    result += f"Выкупов: <b>{sales_count}</b>"
    result += f" ({format(round(stat['sales_sum']), ",d").replace(",", " ")} руб.)\n" if sales_count > 0 else "\n"
    result += f"Отказов: <b>{cancel_count}</b>"
    result += f" ({format(round(stat['orders_cancelled_sum']), ",d").replace(",", " ")} руб.)\n" if cancel_count > 0 else "\n"
    result += f"Возвратов: <b>{return_count}</b>"
    result += f" ({format(round(stat['sales_returned_sum']), ",d").replace(",", " ")} руб.)\n" if return_count > 0 else "\n"
    return result


def format_period_name(period_key: str, date_ranges: dict) -> str:
    start_date, end_date = date_ranges[period_key]
    
    if period_key == 'today':
        day_name = RU_WEEKDAYS[start_date.weekday()]
        return f"Сегодня ({day_name}, {start_date.strftime('%d.%m')})"
    elif period_key == 'yesterday':
        day_name = RU_WEEKDAYS[start_date.weekday()]
        return f"Вчера ({day_name}, {start_date.strftime('%d.%m')})"
    elif period_key in ['current_week']:
        week_number = start_date.isocalendar()[1]
        return f"Текущая неделя - #{week_number} ({start_date.strftime('%d.%m')} - {(end_date - timedelta(days=1)).strftime('%d.%m')})"
    elif period_key in ['last_week']:
        week_number = start_date.isocalendar()[1]
        return f"Прошлая неделя - #{week_number} ({start_date.strftime('%d.%m')} - {(end_date - timedelta(days=1)).strftime('%d.%m')})"
    elif period_key == 'current_month':
        month_name = RU_MONTHS[start_date.month - 1]
        return f"Текущий месяц - {month_name}, {start_date.year}"
    elif period_key == 'last_month':
        month_name = RU_MONTHS[start_date.month - 1]
        return f"Прошлый месяц - {month_name}, {start_date.year}"
    else:
        return period_key  # default fallback