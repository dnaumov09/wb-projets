from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging

from services.scheduler import start_scheduler
from bot.bot import start_bot

from services.sales_service import load_sales


def main():
    init_logging(logging.INFO)
    
    # seller_service.check_and_create_sellers()
    # scheduler.run_remains_updating()

    # load_sales()

    start_scheduler()
    start_bot()
    

if __name__ == "__main__":
    main()
