from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging

from services.scheduler import start_scheduler
from bot.bot import start_bot

from services import reporting_service

from db import functions

from services.scheduler import load_all_data


def main():
    init_logging(logging.INFO)

    load_all_data()

    # reporting_service.update_pipeline_data()

    # start_scheduler()
    # start_bot()
    

if __name__ == "__main__":
    main()
