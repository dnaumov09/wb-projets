from dotenv import load_dotenv
load_dotenv()

import logging_settings
from services import scheduler
from bot import bot
from server import api

def main():
    scheduler.start_scheduler()
    # api.start_api()
    bot.start_bot()


from db.model.seller import get_seller
SELLER = get_seller(1)

def run_tests():
    pass

if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    main()
    
