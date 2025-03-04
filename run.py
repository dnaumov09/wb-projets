from dotenv import load_dotenv
load_dotenv()

from logging_settings import init_logging, logging
import db.init

from services.scheduler import start_scheduler
from bot.bot import start_bot


from api import wb_merchant_api


def main():
    init_logging(logging.INFO)

    start_scheduler()
    start_bot()
    

if __name__ == "__main__":
    main()
