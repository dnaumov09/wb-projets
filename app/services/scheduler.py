import logging
import signal
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services import (
    remains_service,
    card_stat_service,
    cards_service,
    orders_service,
    sales_service,
    advert_service,
    finance_service,
    incomes_services,
    supplies_service,
)

from admin.model import Seller
from admin.services import get_my_seller


MY_SELLER: Seller = get_my_seller()
scheduler = BackgroundScheduler()


# ------------ БЕЗОПАСНЫЙ ВЫЗОВ ------------

def _timed_safe_task(func, *args, **kwargs):
    # start = time.time()
    try:
        func(*args, **kwargs)
    except Exception as e:
        logging.exception(f"[{func.__name__}] error: {e}", exc_info=e)
    # finally:
    #     duration = time.time() - start
    #     logging.info(f"[{func.__name__}] finished in {duration:.2f}s")


# ------------ ОСНОВНЫЕ ЗАДАЧИ ------------

def run_orders_and_sales_updating(seller: Seller, background: bool = False):
    logging.info('run_orders_and_sales_updating - started')
    cards_service.load_cards(seller)
    orders_service.load_orders(seller, background)
    sales_service.load_sales(seller, background)
    logging.info('run_orders_and_sales_updating - done')

def run_keywords_stat_updating(seller: Seller):
    logging.info('run_keywords_stat_updating - started')
    advert_service.load_keywords(seller)
    advert_service.load_keywords_stat(seller)
    logging.info('run_keywords_stat_updating - done')

def run_remains_updating(seller: Seller):
    logging.info('run_remains_updating - started')
    remains_service.load_remains(seller)
    logging.info('run_remains_updating - done')

def run_remains_snapshot_updating(seller: Seller):
    logging.info('run_remains_snapshot_updating - started')
    remains_service.create_remains_snapshot(seller)
    logging.info('run_remains_snapshot_updating - done')

def run_incomes_updating(seller: Seller):
    logging.info('run_incomes_updating - started')
    incomes_services.load_incomes(seller)
    logging.info('run_incomes_updating - done')

def run_finances_updating(seller: Seller):
    logging.info('run_finances_updating - started')
    finance_service.load_finances(seller)
    logging.info('run_finances_updating - done')

def run_topup_adverts():
    logging.info('run_topup_adverts - started')
    advert_service.topup_adverts(MY_SELLER)
    logging.info('run_topup_adverts - done')

def run_stat_updating():
    logging.info('run_stat_updating - started')
    advert_service.load_adverts(MY_SELLER)
    advert_service.load_adverts_stat(MY_SELLER)
    cards_service.load_cards(MY_SELLER)
    card_stat_service.load_cards_stat(MY_SELLER)
    advert_service.process_adverts(MY_SELLER)
    logging.info('run_stat_updating - done')


def run_daily_tasks():
    run_orders_and_sales_updating(MY_SELLER)
    run_incomes_updating(MY_SELLER)
    run_remains_updating(MY_SELLER)
    run_remains_snapshot_updating(MY_SELLER)
    run_keywords_stat_updating(MY_SELLER)


def run_supplies_offices_status_updating(seller: Seller):
    supplies_service.get_supplies_offices_status(seller)


def run_weekly():
    run_daily_tasks()
    run_finances_updating(MY_SELLER)


# ------------ КОНФИГУРАЦИЯ ------------

SCHEDULE_CONFIG = [
    # weekly tasks
    {"func": lambda: run_finances_updating(MY_SELLER), "trigger": CronTrigger(day_of_week="mon", hour=12, minute=0)},

    # daily tasks
    {"func": run_daily_tasks, "trigger": CronTrigger(hour=3, minute=0)},
    {"func": run_topup_adverts, "trigger": CronTrigger(hour=23, minute=55)},
    {"func": run_stat_updating, "trigger": CronTrigger(minute=0)},

    # every 5 minutes
    {"func": lambda: run_orders_and_sales_updating(MY_SELLER), "trigger": CronTrigger(minute="*/5")},

    # every 30 seconds
    # {"func": lambda: run_supplies_offices_status_updating(MY_SELLER), "trigger": IntervalTrigger(seconds=30)},
    {"func": lambda: run_supplies_offices_status_updating(MY_SELLER), "trigger": CronTrigger(second="*/30")}
]


# ------------ ОБЁРТКА И ЗАПУСК ------------

def wrap_job(func):
    return lambda: _timed_safe_task(func)

def run_scheduler():
    for config in SCHEDULE_CONFIG:
        scheduler.add_job(
            func=wrap_job(config["func"]),
            trigger=config["trigger"],
            max_instances=1,
            misfire_grace_time=60
        )

    scheduler.start()
    logging.info("Scheduler started")

    def shutdown(signum, frame):
        logging.info(f"Received signal {signum}, shutting down scheduler...")
        scheduler.shutdown(wait=False)
        logging.info("Scheduler shut down complete.")

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    return scheduler
