import schedule
import time

from processor import load_stat


schedule.every(5).minutes.do(load_stat)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
