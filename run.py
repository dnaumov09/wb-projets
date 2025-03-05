from dotenv import load_dotenv
load_dotenv()

import logging
from logging_settings import init_logging

from services.scheduler import start_scheduler
from bot.bot import start_bot

from api.wb_merchant_api import load_warehouse_remains, load_orders, load_sales, load_cards_stat, load_seller_info
from services.remains import parse_remains_data

from db.models.user import get_admins

from db.models.seller import get_seller

import json
def load_json_data_from_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def main():
    init_logging(logging.INFO)
    start_scheduler()
    # start_bot()
    

if __name__ == "__main__":
    main()
