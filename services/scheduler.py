import schedule
import time
from threading import Thread

from services import notification_service
from services import remains_service
from services import card_stat_service
from services import cards_service
from services import orders_service
from services import sales_service
from services import reporting_service


def init_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    scheduler_thread = Thread(target=init_scheduler)
    scheduler_thread.start()

    schedule.every().day.at("23:30").do(notification_service.notyfy_pipeline)
    
    schedule.every().day.at("06:00").do(remains_service.load_remains)
    schedule.every().day.at("06:30").do(reporting_service.update_remains_data)
    
    schedule.every().day.at("12:00").do(reporting_service.update_pipeline_data)
    schedule.every().day.at("18:00").do(reporting_service.update_pipeline_data)
    schedule.every().day.at("00:00").do(reporting_service.update_pipeline_data)

    
    schedule.every(5).minutes.do(load_all_data)


def load_all_data():
    cards_service.load_cards()
    card_stat_service.load_cards_stat()
    orders_service.load_orders()
    sales_service.load_sales()