from dotenv import load_dotenv
load_dotenv()

import logging_settings
from services import scheduler
from bot import bot

def main():
    scheduler.start_scheduler()
    bot.start_bot()


def run_tests():

    from services import incomes_services
    incomes_services.load_incomes()
    # from services import scheduler
    # card_stat_service.load_cards_stat()
    # scheduler.run_stat_updating()
    # scheduler.run_adverts_stat_updating()
    # scheduler.run_remains_updating()
    # scheduler.run_finances_updating()
    pass
    

if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    run_tests()
    main()
    
