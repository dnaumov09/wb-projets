from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging

from services.scheduler import start_scheduler
from bot.bot import start_bot

from db.models.seller import get_seller

from services.remains_service import load_remains


def main():
    init_logging(logging.INFO)

    # load_remains()

    start_scheduler()
    start_bot()
    

if __name__ == "__main__":
    main()
