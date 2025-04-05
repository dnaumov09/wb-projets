from dotenv import load_dotenv
load_dotenv()

import logging_settings
from services import scheduler
from bot import bot

def main():
    scheduler.start_scheduler()
    bot.start_bot()


def run_tests():
    from services import remains_service
    remains_service.create_remains_snapshot()
    pass
    

if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    run_tests()
    # main()
    
