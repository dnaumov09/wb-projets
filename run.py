from dotenv import load_dotenv
load_dotenv()

import logging_settings
from services import scheduler
from bot import bot

def main():
    scheduler.start_scheduler()
    bot.start_bot()


def run_tests():
    # from api import redis
    # redis.get_cluster(23376017, 'bloom')
    # redis.get_excluded(23376017)
    # from services import finance_service
    # finance_service.load_finances()
    pass
    

if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    # run_tests()
    main()
    
