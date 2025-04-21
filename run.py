from dotenv import load_dotenv
load_dotenv()

import logging_settings
from services import scheduler
from bot import bot

def main():
    scheduler.start_scheduler()
    bot.start_bot()


def run_tests():
    from services.scheduler import run_adverts_stat_updating
    # load_adverts()
    # run_adverts_stat_updating()
    # from services import advert_service
    # advert_service.load_keywords()
    # advert_service.load_keywords_stat()

    # from services import finance_service
    # finance_service.load_finances()

    # from services import remains_service
    # remains_service.load_remains()

    from services.scheduler import run_stat_updating_background
    run_stat_updating_background()

    pass
    

if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    # run_tests()
    main()
    
