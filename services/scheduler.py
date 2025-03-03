import schedule
import time
from threading import Thread

from api import wb_merchant_api
from services.notifications import notify_updated_orders, notify_updated_sales


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
