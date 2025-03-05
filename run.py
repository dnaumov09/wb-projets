from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging
import db.init

from services.scheduler import start_scheduler
from bot.bot import start_bot

from api.wb_merchant_api import load_warehouse_remains, load_orders, load_sales, load_cards_stat
from services.remains import parse_remains_data

import json
def load_json_data_from_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def main():
    init_logging(logging.DEBUG)
    load_orders()
    load_sales()
    load_cards_stat()
    # load_warehouse_remains()
    # start_scheduler()
    # start_bot()
    

if __name__ == "__main__":
    main()
