from dotenv import load_dotenv
load_dotenv()

import utils.logging_settings as logging_settings
import services.scheduler as scheduler
from bot import bot
from web import server

def main():
    scheduler.start_scheduler()
    server.start()
    bot.start_bot()

if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    main()
