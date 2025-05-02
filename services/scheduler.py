import logging
import schedule
import time
from datetime import datetime
from threading import Thread

from bot import notification_service
from services import (
    remains_service,
    card_stat_service,
    cards_service,
    orders_service,
    sales_service,
    reporting_service,
    advert_service,
    finance_service,
    incomes_services,
    supplies_service
)

from admin.db_api import get_sellers, Seller
sellers = get_sellers()


def _run_schedule():
    """Continuously run pending scheduled tasks."""
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    """Initialize and start the scheduler thread and set all jobs."""
    # Start the scheduler loop in a separate daemon thread
    scheduler_thread = Thread(target=_run_schedule, daemon=True)
    scheduler_thread.start()

    # Schedule all jobs
    _schedule_jobs()


def _schedule_jobs():
    """Set up all scheduled jobs."""
    
    # Daily jobs # поменять на понедельники
    schedule.every().monday.at("11:00").do(run_finances_updating)
    
    # Daily jobs
    schedule.every().day.at("23:59").do(notification_service.notyfy_pipeline)
    schedule.every().day.at("03:00").do(_run_daily_task)

    # Every minute at 00 seconds - checking inside the function to align tasks
    schedule.every().minute.at(":00").do(_run_precise_minute_tasks)

    # Multiple times a day for adverts stat updating
    # for time_point in ["00:00", "09:00", "12:00", "15:00", "18:00", "21:00"]:
        # schedule.every().day.at(time_point).do()


def _run_precise_minute_tasks():
    """
    Runs tasks aligned to exact 00 seconds every minute:
    - Every minute task
    - Every 5-minute task (only if minute % 5 == 0)
    """
    now = datetime.now()
    
    # Run every minute task
    _run_every_minute_task()

    # Run every 5 minutes task if aligned
    if now.minute % 5 == 0:
        _run_every_5minutes_task()


def _run_every_minute_task():
    for seller in sellers:
        supplies_service.get_supplies_offices_status(seller)

def _run_every_5minutes_task():
    for seller in sellers:
        run_stat_updating(seller)
        run_adverts_stat_updating(seller)


def _run_daily_task():
    """Task that runs every day at 03:00 seconds."""
    for seller in sellers:
        run_remains_updating(seller)
        run_incomes_updating(seller)
        run_stat_updating_background(seller)
    # reporting_service.update_pipeline_data()


def run_stat_updating(seller: Seller):
    """Update various statistics including cards, orders, and sales."""
    logging.info('scheduler.run_stat_updating() - started')
    cards_service.load_cards(seller)
    card_stat_service.load_cards_stat(seller)
    orders_service.load_orders(seller)
    sales_service.load_sales(seller)
    logging.info('scheduler.run_stat_updating() - done')


def run_stat_updating_background(seller: Seller):
    logging.info('scheduler.run_stat_updating_background() - started')
    orders_service.load_orders(seller, True)
    sales_service.load_sales(seller, True)
    logging.info('scheduler.run_stat_updating_background() - done')


def run_adverts_stat_updating(seller: Seller):
    """Update adverts and their statistics."""
    logging.info('scheduler.run_adverts_stat_updating() - started')
    advert_service.load_adverts(seller)
    advert_service.load_adverts_stat(seller)
    advert_service.load_keywords(seller)
    advert_service.load_keywords_stat(seller)
    logging.info('scheduler.run_adverts_stat_updating() - done')



def run_remains_updating(seller: Seller):
    """Update remains data and related reports."""
    logging.info('scheduler.run_remains_updating() - started')
    remains_service.load_remains(seller)
    remains_service.create_remains_snapshot(seller)
    logging.info('scheduler.run_remains_updating() - done')


def run_incomes_updating(seller: Seller):
    """Update incomes data and related reports."""
    logging.info('scheduler.run_incomes_updating() - started')
    incomes_services.load_incomes(seller)
    logging.info('scheduler.run_incomes_updating() - done')


def run_finances_updating(seller: Seller):
    """Update finances and related reports."""
    logging.info('scheduler.run_finances_updating() - started')
    finance_service.load_finances(seller)
    logging.info('scheduler.run_finances_updating() - done')


def run_all(seller: Seller):
    for s in sellers:
        if sellers and seller.sid == s.sid:
            run_stat_updating(s)
            run_stat_updating_background(s)
            run_incomes_updating(s)
            run_remains_updating(s)
            run_finances_updating(s)
            run_adverts_stat_updating(s)
    