import logging
import schedule
import time
from datetime import datetime
from threading import Thread

from services import (
    notification_service,
    remains_service,
    card_stat_service,
    cards_service,
    orders_service,
    sales_service,
    reporting_service,
    advert_service
)


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
    # Daily jobs
    schedule.every().day.at("03:00").do(run_remains_updating)
    schedule.every().day.at("23:59").do(notification_service.notyfy_pipeline)

    # Every minute at 00 seconds - checking inside the function to align tasks
    schedule.every().minute.at(":00").do(run_precise_minute_tasks)

    # Multiple times a day for adverts stat updating
    for time_point in ["00:00", "09:00", "12:00", "15:00", "18:00", "21:00"]:
        schedule.every().day.at(time_point).do(reporting_service.update_pipeline_data)


def run_precise_minute_tasks():
    """
    Runs tasks aligned to exact 00 seconds every minute:
    - Every minute task
    - Every 5-minute task (only if minute % 5 == 0)
    """
    now = datetime.now()

    # Run every minute task
    run_every_minute_task()

    # Run every 5 minutes task if aligned
    if now.minute % 5 == 0:
        run_every_5minutes_task()


def run_every_minute_task():
    """Task that runs every minute at 00 seconds."""
    pass


def run_every_5minutes_task():
    """Task that runs every 5 minutes at 00 seconds."""
    run_stat_updating()
    run_adverts_stat_updating()
    

def run_stat_updating():
    """Update various statistics including cards, orders, and sales."""
    logging.info('scheduler.run_stat_updating() - started')
    cards_service.load_cards()
    card_stat_service.load_cards_stat()
    orders_service.load_orders()
    sales_service.load_sales()
    logging.info('scheduler.run_stat_updating() - done')


def run_remains_updating():
    """Update remains data and related reports."""
    remains_service.load_remains()
    reporting_service.update_remains_data()


def run_adverts_stat_updating():
    """Update adverts and their statistics."""
    logging.info('scheduler.run_adverts_stat_updating() - started')
    advert_service.load_adverts()
    advert_service.load_adveerts_stat()
    logging.info('scheduler.run_adverts_stat_updating() - done')
