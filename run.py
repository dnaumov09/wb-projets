from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging

from services.scheduler import start_scheduler
from bot.bot import start_bot

from services.orders_service import load_orders


def main():
    init_logging(logging.INFO)
    
    # seller_service.check_and_create_sellers()
    # scheduler.run_remains_updating()

    load_orders()

    # start_scheduler()
    # start_bot()
    

if __name__ == "__main__":
    main()
