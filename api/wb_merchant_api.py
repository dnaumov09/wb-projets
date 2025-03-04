import os
import requests
import logging
from datetime import datetime, time
from db.card import get_all as get_all_cards, save as save_card
from db.order import Order, save_update_orders
from db.sale import Sale, save_update_sales
from db import settings
from services.statistics import save_cards_stat

from ratelimit import limits, sleep_and_retry

WB_MERCHANT_API_TOKEN = os.getenv('WB_MERCHANT_API_TOKEN')
LOAD_ORDERS_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
LOAD_SALES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'
LOAD_CARD_STAT_DAILY_URL = 'https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail/history'

headers = {
    "Authorization": f"Bearer {WB_MERCHANT_API_TOKEN}",
    "Content-Type": "application/json"
}

ONE_MINUTE = 60

cards = get_all_cards()
card_map = {c.nm_id: c for c in get_all_cards()}


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_orders() -> list[Order]:
    logging.info("Loading orders data")
    last_updated = settings.get_orders_last_updated()
    params = {
        "dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), 
        "flag": 0
        }
    
    try:
        response = requests.get(LOAD_ORDERS_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise error for HTTP failures
        data = response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch orders data:\n{e}")
        return

    if not data:
        logging.info("No new orders data")
        return

    logging.info("Orders data received")

    updates = save_update_orders(data, card_map)
    logging.info(f"Orders data saved")
    return updates


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_sales() -> list[Sale]:
    logging.info("Loading sales data")
    last_updated = settings.get_sales_last_updated()
    params = {
        "dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), 
        "flag": 0
        }
    
    try:
        response = requests.get(LOAD_SALES_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise error for HTTP failures
        data = response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch sales data: {e}")
        return
    
    if not data:
        logging.info("No new sales data")
        return
    
    logging.info("Sales data received")

    updates = save_update_sales(data, card_map)
    logging.info(f"Sales data saved until")
    return updates


@sleep_and_retry
@limits(calls=3, period=ONE_MINUTE)
def load_cards_stat():
    logging.info("Loading cards stat data")
    now = datetime.now()
    begin = datetime.combine(settings.get_cards_stat_last_updated(), time.min)
    payload = {
                "nmIDs": [c.nm_id for c in cards],
                "period": {
                    "begin": begin.strftime("%Y-%m-%d"),
                    "end": now.strftime("%Y-%m-%d")
                },
                "aggregationLevel": "day"
              }
    
    try:
        response = requests.post(LOAD_CARD_STAT_DAILY_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise error for HTTP failures
        data = response.json().get('data')
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch cards stat data: {e}")
        return
    
    if not data:
        logging.info("No new cards stat data")
        return
    
    logging.info("Cards stat data received")
    save_cards_stat(data, now)
    logging.info(f"Cards stat data saved until {now}")
