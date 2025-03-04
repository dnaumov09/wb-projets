from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging
import db.init

from services.scheduler import start_scheduler
from bot.bot import start_bot

import api.wb_merchant_api as wb_merchant_api


def main():
    init_logging(logging.INFO)
    wb_merchant_api.load_sales()
    # start_scheduler()
    # start_bot()
    

if __name__ == "__main__":
    main()
