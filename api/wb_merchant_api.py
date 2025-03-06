import os
import requests
import logging
from datetime import datetime, time
from db.models.card import get_seller_cards
from db.models.order import Order, save_update_orders
from db.models.sale import Sale, save_update_sales
from db.models.card_stat import save_update_card_stat
from db.models.seller import Seller
import db.models.settings as settings

from ratelimit import limits, sleep_and_retry


LOAD_SELLER_INFO_URL = 'https://common-api.wildberries.ru/api/v1/seller-info'
LOAD_SELLER_CARDS_URL = 'https://content-api.wildberries.ru/content/v2/get/cards/list'

LOAD_ORDERS_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'

LOAD_SALES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'

LOAD_CARD_STAT_DAILY_URL = 'https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail/history'

CREATE_WAREHOUSE_REMAINS_TASK_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains?groupByBrand={group_by_brand}&groupBySubject={group_by_subject}&groupBySa={group_by_sa}&groupByNm={group_by_nm}&groupByBarcode={group_by_barcode}&groupBySize={group_by_size}'
CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/status'
GET_WAREHOUSE_REMAINS_REPORT_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/download'



ONE_MINUTE = 60


def get_headers(seller: Seller):
    return {
        "Authorization": f"Bearer {seller.token}",
        "Content-Type": "application/json"
    }


def load_seller_info(seller: Seller):
    try:
        response = requests.get(LOAD_SELLER_INFO_URL, headers=get_headers(seller))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch seller info: {e}")


@sleep_and_retry
@limits(calls=100, period=ONE_MINUTE)
def load_seller_cards(seller: Seller):
    try:
        payload = {
            "settings": {                      
                "cursor": {
                    "limit": 100
                },
                "filter": {
                    "withPhoto": -1
                }
            }
        }
        response = requests.post(LOAD_SELLER_CARDS_URL, headers=get_headers(seller), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch seller info: {e}")


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def create_warehouse_remains_task(seller: Seller):
    try:
        response = requests.get(CREATE_WAREHOUSE_REMAINS_TASK_URL.format(
            group_by_brand=True,
            group_by_subject=True,
            group_by_sa=True,
            group_by_nm=True,
            group_by_barcode=True,
            group_by_size=True
        ), headers=get_headers(seller))
        return response.json().get('data').get('taskId')
    except requests.RequestException as e:
        logging.debug(f"Failed to create warehouse remains task: {e}")


@sleep_and_retry
@limits(calls=1, period=5)
def check_warehouse_remains_task_status(seller: Seller, task_id: str):
    try:
        response = requests.get(CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL.format(task_id=task_id), headers=get_headers(seller))
        return response.json().get('data').get('status')
    except requests.RequestException as e:
        logging.debug(f"Failed to check warehouse remains task status: {e}")


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_warehouse_remains_report(seller: Seller, task_id: str):
    try:
        response = requests.get(GET_WAREHOUSE_REMAINS_REPORT_URL.format(task_id=task_id), headers=get_headers(seller))
        return response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to load warehouse remains report: {e}")


#----------------


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_orders(seller: Seller) -> list[Order]:
    logging.info("Loading orders data")
    last_updated = datetime.now()
    params = {
        "dateFrom": settings.get_orders_last_updated().strftime("%Y-%m-%dT%H:%M:%S"), 
        "flag": 0
        }
    
    try:
        response = requests.get(LOAD_ORDERS_URL, headers=get_headers(seller), params=params)
        response.raise_for_status() 
        data = response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch orders data:\n{e}")
        return

    if not data:
        settings.set_orders_last_updated(last_updated)
        logging.info("No new orders data")
        return

    logging.debug("Orders data received")
    card_map = {c.nm_id: c for c in get_seller_cards(seller.id)}
    updates = save_update_orders(data, card_map)
    settings.set_orders_last_updated(last_updated)
    logging.info(f"Orders data saved")
    return updates


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_sales(seller: Seller) -> list[Sale]:
    logging.info("Loading sales data")
    last_updated = datetime.now()
    params = {
        "dateFrom": settings.get_sales_last_updated().strftime("%Y-%m-%dT%H:%M:%S"), 
        "flag": 0
        }
    
    try:
        response = requests.get(LOAD_SALES_URL, headers=get_headers(seller), params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch sales data: {e}")
        return

    if not data:
        settings.set_sales_last_updated(last_updated)
        logging.info("No new sales data")
        return
    
    logging.debug("Sales data received")
    card_map = {c.nm_id: c for c in get_seller_cards(seller.id)}
    updates = save_update_sales(data, card_map)
    settings.set_sales_last_updated(last_updated)
    logging.info(f"Sales data saved until")
    return updates


@sleep_and_retry
@limits(calls=3, period=ONE_MINUTE)
def load_cards_stat(seller: Seller):
    logging.info("Loading cards stat data")
    last_updated = datetime.now()
    begin = datetime.combine(settings.get_cards_stat_last_updated(), time.min)
    card_map = {c.nm_id: c for c in get_seller_cards(seller.id)}
    payload = {
                "nmIDs": list(card_map.keys()),
                "period": {
                    "begin": begin.strftime("%Y-%m-%d"),
                    "end": last_updated.strftime("%Y-%m-%d")
                },
                "aggregationLevel": "day"
              }
    
    try:
        response = requests.post(LOAD_CARD_STAT_DAILY_URL, headers=get_headers(seller), json=payload)
        response.raise_for_status() 
        data = response.json().get('data')
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch cards stat data: {e}")
        return
    
    if not data:
        settings.set_cards_stat_last_updated(last_updated)
        logging.info("No new cards stat data")
        return
    
    logging.debug("Cards stat data received")
    save_update_card_stat(data, last_updated, seller)
    settings.set_cards_stat_last_updated(last_updated)
    logging.info(f"Cards stat data saved")
