from typing import Optional, Dict, Any, List, Union, Literal

import requests
import logging
from datetime import datetime, time
from db.model.card import Card
from db.model.seller import Seller
from db.model.advert import Advert, AdvertType
from bot.notification_service import notify_error

from ratelimit import limits, sleep_and_retry


class MerchantAPIEndpoints:
    LOAD_ORDERS_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
    LOAD_SALES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'
    LOAD_FINANCIAL_REPORT_URL = 'https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod?dateFrom={date_from}&dateTo={date_to}'
    LOAD_INCOMES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/incomes?dateFrom={date_from}'

    LOAD_ADVERTS_COUNT_URL = 'https://advert-api.wildberries.ru/adv/v1/promotion/count'
    LOAD_ADVERTS_INFO_URL = 'https://advert-api.wildberries.ru/adv/v1/promotion/adverts'
    LOAD_ADVERTS_STAT_URL = 'https://advert-api.wildberries.ru/adv/v2/fullstats'
    LOAD_ADVERTS_STAT_WORDS_URL = 'https://advert-api.wildberries.ru/adv/v2/auto/stat-words'
    LOAD_KEYWORDS_STAT_URL = 'https://advert-api.wildberries.ru/adv/v0/stats/keywords'
    UPDATE_ADVERT_BIDS_URL = 'https://advert-api.wildberries.ru/adv/v0/bids'

    LOAD_CARD_STAT_DAILY_URL = 'https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail/history'
    CREATE_WAREHOUSE_REMAINS_TASK_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains?groupByBrand={group_by_brand}&groupBySubject={group_by_subject}&groupBySa={group_by_sa}&groupByNm={group_by_nm}&groupByBarcode={group_by_barcode}&groupBySize={group_by_size}'
    CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/status'
    GET_WAREHOUSE_REMAINS_REPORT_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/download'

    LOAD_WB_OFFICES_URL = "https://marketplace-api.wildberries.ru/api/v3/offices"
    LOAD_WB_WAREHOUSES_URL = "https://supplies-api.wildberries.ru/api/v1/warehouses"
    LOAD_SELLER_INFO_URL = 'https://common-api.wildberries.ru/api/v1/seller-info'
    LOAD_SELLER_CARDS_URL = 'https://content-api.wildberries.ru/content/v2/get/cards/list'

# --- Helpers ---

def get_headers(seller: Seller):
    return {
        "Authorization": f"Bearer {seller.token}",
        "Content-Type": "application/json"
    }


def format_url(template: str, **kwargs) -> str:
    return template.format(**kwargs)


def api_request(
    seller: Seller,
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    url: str,
    params: Optional[Dict[str, Any]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
    timeout: int = 20,
    data_key: Optional[str] = None
) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    headers = get_headers(seller)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_payload,
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        return data.get(data_key) if data_key else data
    except requests.RequestException as e:
        logging.error(f"[{seller.trade_mark}] API {method} request failed at {url}: {e}")
        notify_error(seller, f"API {method} request failed at {url}:\n{e}")
        return None
    

# --- API functions ---

def load_wb_offices(seller: Seller):
    return api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_WB_OFFICES_URL)


def load_wb_warehouses(seller: Seller):
    return api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_WB_WAREHOUSES_URL)


def load_seller_info(seller: Seller):
    return api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_SELLER_INFO_URL)


@sleep_and_retry
@limits(calls=100, period=61)
def load_seller_cards(seller: Seller):
    payload = {
        "settings": {
            "cursor": {"limit": 100},
            "filter": {"withPhoto": -1}
        }
    }
    return api_request(seller, 'POST', MerchantAPIEndpoints.LOAD_SELLER_CARDS_URL, json_payload=payload)


@sleep_and_retry
@limits(calls=1, period=61)
def load_incomes(last_updated: datetime, seller: Seller):
    url = format_url(MerchantAPIEndpoints.LOAD_INCOMES_URL,
                     date_from=last_updated.strftime("%Y-%m-%d"))
    return api_request(seller, 'GET', url)


@sleep_and_retry
@limits(calls=1, period=61)
def create_warehouse_remains_task(seller: Seller):
    url = format_url(MerchantAPIEndpoints.CREATE_WAREHOUSE_REMAINS_TASK_URL,
                     group_by_brand=True,
                     group_by_subject=True,
                     group_by_sa=True,
                     group_by_nm=True,
                     group_by_barcode=True,
                     group_by_size=True)
    result = api_request(seller, 'GET', url, data_key='data')
    return result.get('taskId') if result else None


@sleep_and_retry
@limits(calls=1, period=5)
def check_warehouse_remains_task_status(seller: Seller, task_id: str):
    url = format_url(MerchantAPIEndpoints.CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL, task_id=task_id)
    result = api_request(seller, 'GET', url, data_key='data')
    return result.get('status') if result else None


@sleep_and_retry
@limits(calls=1, period=61)
def load_warehouse_remains_report(seller: Seller, task_id: str):
    url = format_url(MerchantAPIEndpoints.GET_WAREHOUSE_REMAINS_REPORT_URL, task_id=task_id)
    return api_request(seller, 'GET', url)


@sleep_and_retry
@limits(calls=3, period=61)
def load_cards_stat(last_updated: datetime, seller: Seller, seller_cards: list[Card]):
    begin_date = datetime.combine(last_updated, time.min).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    nm_ids = [card.nm_id for card in seller_cards]
    payload = {
        "nmIDs": nm_ids,
        "period": {"begin": begin_date, "end": end_date},
        "aggregationLevel": "day"
    }
    return api_request(seller, 'POST', MerchantAPIEndpoints.LOAD_CARD_STAT_DAILY_URL, json_payload=payload, data_key='data')


@sleep_and_retry
@limits(calls=1, period=61)
def load_fincancial_report(date_from: datetime, date_to: datetime, seller: Seller):
    url = format_url(MerchantAPIEndpoints.LOAD_FINANCIAL_REPORT_URL, 
                     date_from=date_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                     date_to=date_to.strftime("%Y-%m-%dT%H:%M:%S.%f")
                     )
    return api_request(seller, 'GET', url)


@sleep_and_retry
@limits(calls=1, period=61)
def load_orders(last_updated: datetime, seller: Seller):
    params = {"dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), "flag": 0}
    return api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_ORDERS_URL, params=params)


@sleep_and_retry
@limits(calls=1, period=61)
def load_sales(last_updated: datetime, seller: Seller):
    params = {"dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), "flag": 0}
    return api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_SALES_URL, params=params)


@sleep_and_retry
@limits(calls=5, period=1)
def load_adverts(seller: Seller):
    count_response = api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_ADVERTS_COUNT_URL)
    if not count_response or 'adverts' not in count_response:
        return None

    advert_ids = {advert['advertId'] for group in count_response['adverts'] for advert in group['advert_list']}
    if not advert_ids:
        return None

    detail_response = api_request(seller, 'POST', MerchantAPIEndpoints.LOAD_ADVERTS_INFO_URL, json_payload=list(advert_ids))
    return detail_response


@sleep_and_retry
@limits(calls=5, period=1)
def load_adverts_stat(seller: Seller, adverts: list[Advert], last_updated: datetime):
    end_date = datetime.now().strftime("%Y-%m-%d")
    payload = []
    for advert in adverts:
        payload.append({
            "id": advert.advert_id,
            "interval": {
                "begin": last_updated.strftime("%Y-%m-%d"), 
                "end": end_date
            }
        })
    detail_response = api_request(seller, 'POST', MerchantAPIEndpoints.LOAD_ADVERTS_STAT_URL, json_payload=payload)
    return detail_response

@sleep_and_retry
@limits(calls=4, period=1)
def load_adverts_stat_words(seller: Seller, advert: Advert):
    return api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_ADVERTS_STAT_WORDS_URL, params={"id": advert.advert_id})


@sleep_and_retry
@limits(calls=4, period=1)
def load_keywords_stat(seller: Seller, advert: Advert, date_from: datetime, date_to: datetime):
    params = {
        "advert_id": advert.advert_id, 
        'from': date_from.strftime("%Y-%m-%d"), 
        'to': date_to.strftime("%Y-%m-%d")
        }
    return api_request(seller, 'GET', MerchantAPIEndpoints.LOAD_KEYWORDS_STAT_URL, params=params)


@sleep_and_retry
@limits(calls=4, period=1)
def update_advert_bids(seller: Seller, data):
    payload = {
        "bids": [
            {
                "advert_id": item["advert_id"],
                "nm_bids": [
                    {"nm": bid["nm_id"], "bid": bid["bid"]}
                    for bid in item["bids"]
                ]
            }
            for item in data
        ]
    }
            
    return api_request(seller, 'PATCH', MerchantAPIEndpoints.UPDATE_ADVERT_BIDS_URL, json_payload=payload)