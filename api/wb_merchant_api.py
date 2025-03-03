import os
import requests
import logging
from datetime import datetime, time
from db.card import get_all as get_all_cards, save as save_card
from db.order import Order, save as save_order
from db.sale import save as save_sale
from db.card_stat import save as save_card_stat
from db import settings

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


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_orders() -> list[Order]:
    logging.info("Loading orders data")
    now = datetime.now()
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

    updates = []
    card_map = {c.nm_id: c for c in cards}
    for item in data:
        card = card_map.get(item.get('nmId'))
        order = save_order(
            item.get('date'), item.get('lastChangeDate'), item.get('warehouseName'), item.get('warehouseType'),
            item.get('countryName'), item.get('oblastOkrugName'), item.get('regionName'), item.get('supplierArticle'),
            card, item.get('barcode'), item.get('category'), item.get('subject'), item.get('brand'),
            item.get('techSize'), item.get('incomeID'), item.get('isSupply'), item.get('isRealization'),
            item.get('totalPrice'), item.get('discountPercent'), item.get('spp'), item.get('finishedPrice'),
            item.get('priceWithDisc'), item.get('isCancel'), item.get('cancelDate'), item.get('orderType'),
            item.get('sticker'), item.get('gNumber'), item.get('srid')
        )
        updates.append(order)
    logging.info(f"Orders data saved until {now}")
    settings.set_orders_last_updated(now)
    return updates


@sleep_and_retry
@limits(calls=1, period=ONE_MINUTE)
def load_sales():
    logging.info("Loading sales data")
    now = datetime.now()
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

    updates = []
    card_map = {c.nm_id: c for c in cards}
    for item in data:
        card = card_map.get(item.get('nmId'))
        sale = save_sale(
            item.get('date'), item.get('lastChangeDate'), item.get('warehouseName'), item.get('warehouseType'),
            item.get('countryName'), item.get('oblastOkrugName'), item.get('regionName'), item.get('supplierArticle'),
            card, item.get('barcode'), item.get('category'), item.get('subject'), item.get('brand'),
            item.get('techSize'), item.get('incomeID'), item.get('isSupply'), item.get('isRealization'),
            item.get('totalPrice'), item.get('discountPercent'), item.get('spp'), item.get('forPay'),
            item.get('finishedPrice'), item.get('priceWithDisc'), item.get('saleID'), item.get('orderType'),
            item.get('sticker'), item.get('gNumber'), item.get('srid'))
        updates.append(sale)
    logging.info(f"Sales data saved until {now}")
    settings.set_sales_last_updated(now)
    return updates


@sleep_and_retry
@limits(calls=3, period=ONE_MINUTE)
def load_cards_stat():
    logging.info("Loading cards stat data")
    now = datetime.now()
    now_begin = datetime.combine(now, time.min)
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

    card_map = {c.nm_id: c for c in cards}
    for item in data:
        card = card_map.get(item.get('nmID'))
        history = item.get('history')
        for day in history:
            dt = datetime.strptime(day.get('dt'), "%Y-%m-%d")
            dt_end = datetime.combine(dt, time.max) if dt < now_begin else now
            save_card_stat(
                dt,  dt_end, card, day.get('openCardCount'), day.get('addToCartCount'), day.get('ordersCount'),
                day.get('ordersSumRub'), day.get('buyoutsCount'), day.get('buyoutsSumRub'), day.get('cancelCount'), day.get('cancelSumRub')
                )
    

    logging.info(f"Cards stat data saved until {now}")
    settings.set_cards_stat_last_updated(now)
