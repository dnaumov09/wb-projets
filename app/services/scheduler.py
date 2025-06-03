import logging
import schedule
import time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from bot import notification_service
from services import (
    remains_service,
    card_stat_service,
    cards_service,
    orders_service,
    sales_service,
    advert_service,
    finance_service,
    incomes_services,
    supplies_service
)

from admin.model import Seller
from admin.services import get_all_sellers, get_my_seller

MY_SELLER = get_my_seller()
executor = ThreadPoolExecutor(max_workers=10)


def safe_task(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error in {func.__name__}: {e}")


def _run_schedule():
    while True:
        schedule.run_pending()
        next_run = schedule.idle_seconds()
        if next_run is None:
            time.sleep(60)
        else:
            time.sleep(min(next_run, 60))


def start_scheduler():
    scheduler_thread = Thread(target=_run_schedule, daemon=True)
    scheduler_thread.start()
    _schedule_jobs()


def _schedule_jobs():
    daily_jobs = [
        ("03:00", run_daily_task),
        ("23:55", run_topup_adverts), # пополняем в конце дня на след день (в методе сразу добавлен 1 день)
    ]

    for time_str, func in daily_jobs:
        schedule.every().day.at(time_str).do(func)


    for seconds in [":00", ":20", ":40"]:
        schedule.every().minute.at(seconds).do(run_tasks)


def run_tasks():
    now = datetime.now()

    _run_task()

    if now.second == 0:
        _run_every_minute_task()

        if now.minute % 5 == 0:
            _run_every_5minutes_task()


def _run_task():
    executor.submit(safe_task, supplies_service.get_supplies_offices_status, MY_SELLER)


def _run_every_minute_task():
    pass


def _run_every_5minutes_task():
    executor.submit(safe_task, run_orders_and_sales_updating, MY_SELLER)


def run_daily_task():
    for seller in get_all_sellers():
        executor.submit(safe_task, run_orders_and_sales_updating, seller, True)
        executor.submit(safe_task, run_incomes_updating, seller)
        executor.submit(safe_task, run_remains_updating, seller)
        executor.submit(safe_task, run_remains_snapshot_updating, seller)
        executor.submit(safe_task, run_keywords_stat_updating, seller)


def run_orders_and_sales_updating(seller: Seller, background: bool = False):
    logging.info('scheduler.run_orders_and_sales_updating() - started')
    cards_service.load_cards(seller)
    orders_service.load_orders(seller, background)
    sales_service.load_sales(seller, background)
    logging.info('scheduler.run_orders_and_sales_updating() - done')


def run_keywords_stat_updating(seller: Seller):
    logging.info('scheduler.run_keywords_stat_updating() - started')
    advert_service.load_keywords(seller)
    advert_service.load_keywords_stat(seller)
    logging.info('scheduler.run_keywords_stat_updating() - done')


def run_remains_updating(seller: Seller):
    logging.info('scheduler.run_remains_updating() - started')
    remains_service.load_remains(seller)
    logging.info('scheduler.run_remains_updating() - done')


def run_remains_snapshot_updating(seller: Seller):
    logging.info('scheduler.run_remains_snapshot_updating() - started')
    remains_service.create_remains_snapshot(seller)
    logging.info('scheduler.run_remains_snapshot_updating() - done')


def run_incomes_updating(seller: Seller):
    logging.info('scheduler.update_incomes() - started')
    incomes_services.load_incomes(seller)
    logging.info('scheduler.run_incomes_updating() - done')


def run_finances_updating(seller: Seller):
    logging.info('scheduler.run_finances_updating() - started')
    finance_service.load_finances(seller)
    logging.info('scheduler.run_finances_updating() - done')


def run_topup_adverts():
    logging.info('scheduler.run_topup_adverts() - started')
    advert_service.topup_adverts(MY_SELLER)
    logging.info('scheduler.run_topup_adverts() - done')


def run_stat_updating():
    logging.info('scheduler.run_process_adverts() - started')
    advert_service.load_adverts(MY_SELLER)
    advert_service.load_adverts_stat(MY_SELLER)
    
    cards_service.load_cards(MY_SELLER)
    card_stat_service.load_cards_stat(MY_SELLER)
    
    advert_service.process_adverts(MY_SELLER)
    logging.info('scheduler.run_process_adverts() - done')


def run_all():
    run_orders_and_sales_updating(MY_SELLER)
    run_orders_and_sales_updating(MY_SELLER, True)

    run_stat_updating(MY_SELLER)

    run_incomes_updating(MY_SELLER)
    run_remains_updating(MY_SELLER)
    run_remains_snapshot_updating(MY_SELLER)
    
    run_finances_updating(MY_SELLER)
