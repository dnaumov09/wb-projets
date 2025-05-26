from bot.bot import send_message
from datetime import datetime

from db.model.order import Order, OrderStatus
from db.model.sale import Sale, SaleStatus

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from admin.model import Seller

from bot.stat_handler import build_pipeline_data


order_status_messages = {
        # OrderStatus.NEW: "📩 <b>Поступил новый заказ</b>",
        # OrderStatus.ACCEPTED_TO_WH: "📦 <b>Заказ принят складом</b>",
        # OrderStatus.CANCELLED: "➖ <b>Клиент отменил заказ</b>",
        # OrderStatus.UNDEFINED: "❓ <b>Статус заказа не определен</b>"
    }

sales_status_messages = {
        SaleStatus.UNDEFINED: "❓ <b>Статус выкупа не определен</b>",
        SaleStatus.NEW: "✅ <b>Клиент выкупил товар</b>",
        SaleStatus.RETURN: "❌ <b>Клиент вернул заказ</b>"
    }

admins_to_notify = []


def notify_updated_orders(orders: list[Order]):
    if not orders:
        return
    for order in orders:
        if order.status in order_status_messages:
            text = order_status_messages[order.status].format(order.id) + "\n\n" + build_order_data(order)

            for user in admins_to_notify:
                send_message(chat_id=user.tg_chat_id, text=text, disable_notifications=True)


def notify_updated_sales(sales: list[Sale]):
    if not sales:
        return
    for sale in sales:
        if sale.status in sales_status_messages:
            text = sales_status_messages[sale.status].format(sale.id) + "\n\n" + build_sale_data(sale)

            for user in admins_to_notify:
                send_message(chat_id=user.tg_chat_id, text=text)


def notyfy_pipeline():
     for user in admins_to_notify:
        send_message(chat_id=user.tg_chat_id, text=(
            '📈 <b>Динамика продаж</b>'
            '\n\n' + build_pipeline_data()
        ))


def build_order_data(order: Order) -> str:
    result = f"Товар: <b>{order.supplier_article}</b>"
    result += "\n"
    result += f"Сумма: <b>{order.price_with_disc}</b>"
    result += "\n"
    result += f"Регион: <b>{order.region_name}, {order.oblast_okrug_name}</b>"
    result += "\n"
    result += f"Со склада: <b>{order.warehouse_name}</b>"
    result += "\n\n"
    result += f"<i>Дата заказа: <b>{order.date.strftime('%d.%m.%Y %H:%M:%S')}</b></i>"
    # result += "\n"
    # result += f"<i>Обновлено: <b>{order.last_change_date.strftime('%d.%m.%Y %H:%M:%S')}</b></i>"
    # result += "\n"
    # result += f"<i>ID заказа: <b>{order.id if order.id is not None else "---"}</b></i>"
    return result


def build_sale_data(sale: Sale) -> str:
    result = f"Товар: <b>{sale.supplier_article}</b>"
    result += "\n"
    result += f"Сумма: <b>{sale.price_with_disc}</b>"
    result += "\n"
    result += f"Регион: <b>{sale.region_name}, {sale.oblast_okrug_name}</b>"
    result += "\n"
    result += f"Со склада: <b>{sale.warehouse_name}</b>"
    result += "\n\n"
    result += f"<i>Дата выкупа: <b>{sale.date.strftime('%d.%m.%Y %H:%M:%S')}</b></i>"
    # result += "\n"
    # result += f"<i>Обновлено: <b>{sale.last_change_date.strftime('%d.%m.%Y %H:%M:%S')}</b></i>"
    # result += "\n"
    # result += f"<i>ID выкупа: <b>{sale.id if sale.id is not None else "---"}</b></i>"
    return result


def notify_error(seller: Seller, text: str):
    send_message(chat_id=102421129, text=(
        f'‼️ <b>Error ({seller.trade_mark}):</b>'
        '\n\n'
        f'{text}'
    ))


def notify_new_supply_slot(seller: Seller, date: datetime, warehouse_name: str, supply_id: str, coefficient: int, acceptance_cost: float, real: bool):
    dt_day = date.strftime("%A")
    dt_day = dt_day[0].upper() + dt_day[1:]
    dt_date = date.strftime("%d.%m, %Y")

    text = (
        ('🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n\n' if real else '') +
        f'🗓️ <b>Новый слот для поставки{" №" + str(supply_id) if real else ""}:</b>\n\n'
        f'<b>{dt_day} - {dt_date}</b>\n'
        f'Склад: {warehouse_name}\n\n'
        f'Коэф. логистики: {coefficient}\n'
        f'Приёмка: {acceptance_cost} ₽'
    )

    if real:
        url = f"https://seller.wildberries.ru/supplies-management/all-supplies/supply-detail?preorderId=${supply_id}"
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="К поставке", url=url)]])
    else:
        markup = None

    for user in seller.users:
        if user.receive_supplies_statuses:
            send_message(chat_id=user.tg_chat_id, text=text, reply_markup=markup)