import schedule
import time
from threading import Thread

from db.order import Order, OrderStatus
from db.sale import Sale, SaleStatus
from db.user import get_admins

from api import wb_merchant_api
from bot.bot import send_message


CHAT_IDS = [102421129] #[a.chat_id for a in get_admins()]

def init_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    scheduler_thread = Thread(target=init_scheduler)
    scheduler_thread.start()

    schedule.every(5).minutes.do(load_orders)
    schedule.every(5).minutes.do(load_sales)
    schedule.every(5).minutes.do(load_cards_stat)


def load_orders():
    updates = wb_merchant_api.load_orders()
    if updates:
        notify_updated_orders(updates)


def load_sales():
    updates = wb_merchant_api.load_sales()
    if updates:
        notify_updated_sales(updates)


def load_cards_stat():
    wb_merchant_api.load_cards_stat()


def notify_updated_orders(orders: list[Order]):
    for order in orders:
        if order.status == OrderStatus.NEW:
            text = f"✅ <b>Новый заказ (ID: {order.id}):</b>"
        elif order.status == OrderStatus.ACCEPTED_TO_WH:
            return #Skip status # text = f"📦 <b>Заказ принят складом (ID: {order.id}):</b>"
        elif order.status == OrderStatus.CANCELLED:
            text = f"❌ <b>Заказ отменен (ID: {order.id}):</b>"
        else:
            text = f"❓ <b>Статус заказа не определен (ID: {order.id}):</b>"
        
        text += "\n\n" + build_order_data(order) 

        for chat_id in CHAT_IDS:
            send_message(chat_id=chat_id, text=text)


def notify_updated_sales(sales: list[Sale]):
    for sale in sales:
        if sale.status == SaleStatus.NEW:
            text = f"🍺 <b>Новый выкуп ({sale.id}):</b>"
        else:
            text = f"❓ <b>Cтатус выкупа не определен (ID: {sale.id}):</b>"

        text += "\n\n" + build_sale_data(sale)  
    
        for chat_id in CHAT_IDS:
            send_message(chat_id=chat_id, text=text)


def build_order_data(order: Order) -> str:
    text = f"Товар: <b>{order.supplier_article}</b>\n"
    text += f"Сумма: <b>{order.price_with_disc}</b>\n"
    text += f"Регион: <b>{order.region_name}, {order.oblast_okrug_name}</b>\n"
    text += f"Со склада: <b>{order.warehouse_name}</b>\n\n"
    text += f"<i>Дата заказа: <b>{order.date}</b></i>\n"
    text += f"<i>Дата изменения информации: <b>{order.last_change_date}</b></i>"
    return text


def build_sale_data(sale: Sale) -> str:
    text = f"Товар: <b>{sale.supplier_article}</b>\n"
    text += f"Сумма: <b>{sale.price_with_disc}</b>\n"
    text += f"Регион: <b>{sale.region_name}, {sale.oblast_okrug_name}</b>\n"
    text += f"Со склада: <b>{sale.warehouse_name}</b>\n\n"
    text += f"<i>Дата выкупа: <b>{sale.date}</b></i>\n"
    text += f"<i>Дата изменения информации: <b>{sale.last_change_date}</b></i>"
    return text