from aiogram import Router
from aiogram.filters import Command
from datetime import datetime, timedelta
import locale

from aiogram.types import Message

from services.statistics import get_today_stat, get_yesterday_stat, get_current_week_stat, get_current_month_stat

router = Router()

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
months_nominative = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь"
}


@router.message(Command('pipeline'))
async def cmd_pipeline(message: Message):
    now = datetime.now()

    await message.answer("💰 <b>Воронка продаж</b>")
    result = build_daily_stat('Сегодня', now, get_today_stat()[0])
    result += "\n\n" + build_daily_stat('Вчера', now - timedelta(days=1), get_yesterday_stat()[0])
    result += "\n\n" + build_weekly_stat(now, get_current_week_stat()[0])
    result += "\n\n" + build_monthly_stat(now, get_current_month_stat()[0])
    await message.answer(result)


# @router.message(Command('pipeline_detailed'))
# async def cmd_pipeline_detailed(message: Message):
#     now = datetime.now()

#     await message.answer("📊 <b>Воронка продаж (по товарам)</b>")

#     today_stat = get_today_stat(is_detailed=True)
#     yesterday_stat = get_yesterday_stat(is_detailed=True)
#     week_stat = get_current_week_stat(is_detailed=True)
#     month_stat = get_current_month_stat(is_detailed=True)

#     for i in range(len(month_stat)):
#         result = f"<b>{month_stat[i]['title']} ({month_stat[i]['vendor_code']})</b>"
#         result += "\n\n" + build_daily_stat('Сегодня', now, today_stat[i], True)
#         result += "\n\n" + build_daily_stat('Вчера', now - timedelta(days=1), yesterday_stat[i], True)
#         result += "\n\n" + build_weekly_stat(now, week_stat[i], True)
#         result += "\n\n" + build_monthly_stat(now, month_stat[i], True)    
#         await message.answer(result)


def build_daily_stat(when, day, stat, is_detailed: bool = False) -> str:
    day_str = day.strftime("%d.%m - %A")
    date_part, weekday_name = day_str.split(" - ")

    period_details = f"{weekday_name.capitalize()}, {date_part}"
    result = f"<b>{when} ({period_details}):</b>\n"
    result += build_stat_data(stat, is_detailed)
    return result


def build_weekly_stat(day, stat, is_detailed: bool = False) -> str:
    weekday = day.weekday()
    monday = day - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)

    result = f"<b>Неделя #{day.isocalendar()[1]} ({monday.strftime('%d.%m')} - {sunday.strftime('%d.%m')}):</b>\n"
    result += build_stat_data(stat, is_detailed)
    return result


def build_monthly_stat(day, stat, is_detailed: bool = False) -> str:
    result = f"<b>{months_nominative[day.month]}, {day.year}:</b>\n"
    result += build_stat_data(stat, is_detailed)
    return result


def build_stat_data(stat, is_detailed: bool = False) -> str:
    oreders_count = stat['orders_count'] if stat['orders_count'] else 0
    sales_count = stat['sales_count'] if stat['sales_count'] else 0
    cancel_count = stat['orders_cancelled_count'] if stat['orders_cancelled_count'] else 0

    result = ""
    if is_detailed:
        result += f"Открытий карточки: <b>{stat['open_card_count'] if stat['open_card_count'] else 0}</b>\n"
        result += f"Добавлений в корзину: <b>{stat['add_to_cart_count'] if stat['add_to_cart_count'] else 0}</b>\n"

    result += f"Заказов: <b>{oreders_count}</b>"
    result += f" ({format(round(stat['orders_sum']), ",d").replace(",", " ")} руб.)\n" if oreders_count > 0 else "\n"
    result += f"Выкупов: <b>{sales_count}</b>"
    result += f" ({format(round(stat['sales_sum']), ",d").replace(",", " ")} руб.)\n" if sales_count > 0 else "\n"
    result += f"Количество отказов: <b>{cancel_count}</b>"
    result += f" ({format(round(stat['orders_cancelled_sum']), ",d").replace(",", " ")} руб.)\n" if cancel_count > 0 else "\n"
    return result
