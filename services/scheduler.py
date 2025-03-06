import schedule
import time
from threading import Thread

from services.notification_service import notyfy_pipeline
from services.remains_service import load_remains
from services.cards_service import load_cards_stat
from services.orders_service import load_orders
from services.sales_service import load_sales


def init_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    scheduler_thread = Thread(target=init_scheduler)
    scheduler_thread.start()

    schedule.every().day.at("23:30").do(notyfy_pipeline)
    schedule.every().day.at("06:00").do(load_remains)
    
    schedule.every(5).minutes.do(load_cards_stat)
    schedule.every(5).minutes.do(load_orders)
    schedule.every(5).minutes.do(load_sales)
