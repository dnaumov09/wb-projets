import schedule
import time
from threading import Thread

from api import wb_merchant_api
from services.notifications import notify_updated_orders, notify_updated_sales, notyfy_pipeline

from db.models.seller import get_seller
seller = get_seller(1)


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

    schedule.every().day.at("09:00").do(load_warehouse_remains)
    schedule.every().day.at("23:30").do(notyfy_pipeline)


def load_orders():
    updates = wb_merchant_api.load_orders(seller)
    if updates:
        notify_updated_orders(updates)


def load_sales():
    updates = wb_merchant_api.load_sales(seller)
    if updates:
        notify_updated_sales(updates)


def load_cards_stat():
    wb_merchant_api.load_cards_stat(seller)


def load_warehouse_remains():
    wb_merchant_api.load_warehouse_remains(seller)
