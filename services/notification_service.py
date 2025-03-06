from datetime import datetime

from db.models.user import get_admins
from bot.bot import send_message

from db.models.order import Order, OrderStatus
from db.models.sale import Sale, SaleStatus

from bot.stat_handler import build_pipeline_data


order_status_messages = {
        OrderStatus.NEW: "✅ <b>Новый заказ (ID: {}):</b>",
        # OrderStatus.ACCEPTED_TO_WH: "📦 <b>Заказ принят складом (ID: {}):</b>",
        OrderStatus.CANCELLED: "❌ <b>Заказ отменен (ID: {}):</b>",
        OrderStatus.UNDEFINED: "❓ <b>Статус заказа не определен (ID: {}):</b>"
    }

sales_status_messages = {
        SaleStatus.NEW: "✅ <b>Новый заказ (ID: {}):</b>",
        SaleStatus.UNDEFINED: "❓ <b>Статус заказа не определен (ID: {}):</b>"
    }

admins_to_notify = [user for user in get_admins() if user.receive_orders]


def notify_updated_orders(orders: list[Order]):
    for order in orders:
        if order.status in order_status_messages:
            text = order_status_messages[order.status].format(order.id) + "\n\n" + build_order_data(order)

            for user in admins_to_notify:
                send_message(chat_id=user.tg_chat_id, text=text)


def notify_updated_sales(sales: list[Sale]):
    for sale in sales:
        if sale.status in sales_status_messages:
            text = sales_status_messages[sale.status].format(sale.id) + "\n\n" + build_sale_data(sale)

            for user in admins_to_notify:
                send_message(chat_id=user.tg_chat_id, text=text)


def notyfy_pipeline():
     for user in admins_to_notify:
        send_message(chat_id=user.tg_chat_id, text="💰 <b>Воронка продаж</b>")
        send_message(chat_id=user.tg_chat_id, text=build_pipeline_data())


def build_order_data(order: Order) -> str:
    return (
        f"Товар: <b>{order.supplier_article}</b>\n"
        f"Сумма: <b>{order.price_with_disc}</b>\n"
        f"Регион: <b>{order.region_name}, {order.oblast_okrug_name}</b>\n"
        f"Со склада: <b>{order.warehouse_name}</b>\n\n"
        f"<i>Дата заказа: <b>{order.date}</b></i>\n"
        f"<i>Дата изменения информации: <b>{order.last_change_date}</b></i>"
    )


def build_sale_data(sale: Sale) -> str:
    return (
        f"Товар: <b>{sale.supplier_article}</b>\n"
        f"Сумма: <b>{sale.price_with_disc}</b>\n"
        f"Регион: <b>{sale.region_name}, {sale.oblast_okrug_name}</b>\n"
        f"Со склада: <b>{sale.warehouse_name}</b>\n\n"
        f"<i>Дата выкупа: <b>{sale.date}</b></i>\n"
        f"<i>Дата изменения информации: <b>{sale.last_change_date}</b></i>"
    )