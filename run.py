from dotenv import load_dotenv
load_dotenv()

from threading import Thread

import db.init
import scheduler
from bot import bot

def main():
    thread = Thread(target=scheduler.run_scheduler)
    thread.start()

    bot.run_bot()
    

if __name__ == "__main__":
    main()
