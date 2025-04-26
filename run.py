from dotenv import load_dotenv
load_dotenv()

import logging_settings
from services import scheduler
from bot import bot
from server import api

def main():
    scheduler.start_scheduler()
    bot.start_bot()

if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    main()
