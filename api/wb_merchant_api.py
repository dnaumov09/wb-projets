from typing import Optional, Dict, Any, List

import requests
import logging
from datetime import datetime, time
from db.models.card import get_seller_cards
from db.models.seller import Seller

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
    logging.info(f"Loading cards for {seller.trade_mark}")
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
        data = response.json()
    except requests.RequestException as e:
        logging.debug(f"Failed to fetch cards info: {e}")

    if not data:
        logging.info("No cards data")
        return
    
    logging.info("Cards received")
    return data


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


@sleep_and_retry
@limits(calls=3, period=ONE_MINUTE)
def load_cards_stat(last_updated: datetime, seller: Seller) -> Optional[List[Dict[str, Any]]]:
    logging.info(f"Loading cards stat for {seller.trade_mark}")
    
    begin_date = datetime.combine(last_updated, time.min).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    seller_cards = get_seller_cards(seller.id)
    if not seller_cards:
        logging.info("No cards found for seller.")
        return None

    card_map = {card.nm_id: card for card in seller_cards}
    nm_ids = list(card_map.keys())

    payload = {
        "nmIDs": nm_ids,
        "period": {
            "begin": begin_date,
            "end": end_date
        },
        "aggregationLevel": "day"
    }

    try:
        response = requests.post(
            LOAD_CARD_STAT_DAILY_URL,
            headers=get_headers(seller),
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        data = response.json().get('data', [])
    except requests.RequestException as e:
        logging.error(f"Failed to fetch cards stat: {e}")
        return None

    if not data:
        logging.info("No new cards stat")
        return None

    logging.info(f"Cards stat received: {len(data)} records")
    return data


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_orders(last_updated: datetime, seller: Seller) -> Optional[Dict[str, Any]]:
    logging.info(f"Loading orders for {seller.trade_mark}")

    params = {
        "dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"),
        "flag": 0
    }

    try:
        response = requests.get(
            LOAD_ORDERS_URL,
            headers=get_headers(seller),
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch orders: {e}")
        return None

    if not data:
        logging.info("No new orders")
        return None

    logging.info(f"Orders received: {len(data)} records")
    return data


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_sales(last_updated: datetime, seller: Seller) -> Optional[Dict[str, Any]]:
    logging.info(f"Loading sales for {seller.trade_mark}")

    params = {
        "dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"),
        "flag": 0
    }

    try:
        response = requests.get(
            LOAD_SALES_URL,
            headers=get_headers(seller),
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch sales: {e}")
        return None

    if not data:
        logging.info("No new sales")
        return None

    logging.info(f"Sales received: {len(data)} records")
    return data
