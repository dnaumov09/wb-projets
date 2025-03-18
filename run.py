from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging

from services.scheduler import start_scheduler
from bot.bot import start_bot

from services import finance_service


def main():
    init_logging(logging.INFO)

    finance_service.load_finances()

    start_scheduler()
    start_bot()
    

if __name__ == "__main__":
    main()
