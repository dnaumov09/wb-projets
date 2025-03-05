import os
import requests
import logging
import time as t
from datetime import datetime, time
from db.card import get_all as get_all_cards, save as save_card
from db.order import Order, save_update_orders
from db.sale import Sale, save_update_sales
from db import settings
from services.statistics import save_cards_stat
from services.remains import parse_remains_data

from ratelimit import limits, sleep_and_retry


WB_MERCHANT_API_TOKEN = os.getenv('WB_MERCHANT_API_TOKEN')
LOAD_ORDERS_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
LOAD_SALES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'
LOAD_CARD_STAT_DAILY_URL = 'https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail/history'
CREATE_WAREHOUSE_REMAINS_TASK_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains?groupByBrand={group_by_brand}&groupBySubject={group_by_subject}&groupBySa={group_by_sa}&groupByNm={group_by_nm}&groupByBarcode={group_by_barcode}&groupBySize={group_by_size}'
CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/status'
GET_WAREHOUSE_REMAINS_REPORT_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/download'


headers = {
    "Authorization": f"Bearer {WB_MERCHANT_API_TOKEN}",
    "Content-Type": "application/json"
}

ONE_MINUTE = 60

cards = get_all_cards()
card_map = {c.nm_id: c for c in get_all_cards()}


def load_warehouse_remains():
    logging.info("Creating warehouse remains task")
    try:
        response = requests.get(CREATE_WAREHOUSE_REMAINS_TASK_URL.format(
            group_by_brand=True,
            group_by_subject=True,
            group_by_sa=True,
            group_by_nm=True,
            group_by_barcode=True,
            group_by_size=True
        ), headers=headers)
        response.raise_for_status()
        task_id = response.json().get('data').get('taskId')
        logging.debug(f"Task ID: {task_id}")
        while True:
            t.sleep(5)
            response = requests.get(CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL.format(task_id=task_id), headers=headers)
            response.raise_for_status()
            status = response.json().get('data').get('status')
            logging.debug(f"Task status: {status}")
            if status == 'done':
                logging.debug("Warehouse remains loading...")
                response = requests.get(GET_WAREHOUSE_REMAINS_REPORT_URL.format(task_id=task_id), headers=headers)
                response.raise_for_status()
                parse_remains_data(response.json())
                break
    except requests.RequestException as e:
        logging.debug(f"Failed to create warehouse remains task: {e}")
        return

    logging.info("Warehouse remains loaded")


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
    
    last_updated = datetime.now()

    if not data:
        settings.set_orders_last_updated(last_updated)
        logging.info("No new orders data")
        return

    logging.debug("Orders data received")
    updates = save_update_orders(data, card_map)
    settings.set_orders_last_updated(last_updated)
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
    
    last_updated = datetime.now()
    

    if not data:
        settings.set_sales_last_updated(last_updated)
        logging.info("No new sales data")
        return
    
    logging.debug("Sales data received")
    updates = save_update_sales(data, card_map)
    settings.set_sales_last_updated(last_updated)
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
        settings.set_cards_stat_last_updated(now)
        logging.info("No new cards stat data")
        return
    
    logging.debug("Cards stat data received")
    save_cards_stat(data, now)
    settings.set_cards_stat_last_updated(now)
    logging.info(f"Cards stat data saved until {now}")
