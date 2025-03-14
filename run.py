from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging

from services.scheduler import start_scheduler
from bot.bot import start_bot

from services.remains_service import load_remains
from services.reporting_service import update_remains_data
from services import scheduler
from services import remains_service


def main():
    init_logging(logging.INFO)
    
    # seller_service.check_and_create_sellers()
    # remains_service.load_warehouses()
    # scheduler.run_remains_updating()

    # load_sales()
    # load_cards()
    # load_remains()
    # update_remains_data()

    start_scheduler()
    start_bot()
    

if __name__ == "__main__":
    main()
