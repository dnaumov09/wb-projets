import requests
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any, List, Union, Literal
from ratelimit import limits, sleep_and_retry

from db.model.card import Card
from db.model.seller import Seller
from db.model.advert import Advert
from bot.notification_service import notify_error

class MerchantAPIEndpoints:
    LOAD_WB_OFFICES_URL = "https://marketplace-api.wildberries.ru/api/v3/offices"
    LOAD_WB_WAREHOUSES_URL = "https://supplies-api.wildberries.ru/api/v1/warehouses"
    LOAD_SELLER_INFO_URL = 'https://common-api.wildberries.ru/api/v1/seller-info'
    LOAD_SELLER_CARDS_URL = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    LOAD_ORDERS_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
    LOAD_SALES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/sales'
    LOAD_CARD_STAT_DAILY_URL = 'https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail/history'
    LOAD_ADVERTS_COUNT_URL = 'https://advert-api.wildberries.ru/adv/v1/promotion/count'
    LOAD_ADVERTS_INFO_URL = 'https://advert-api.wildberries.ru/adv/v1/promotion/adverts'
    LOAD_ADVERTS_STAT_URL = 'https://advert-api.wildberries.ru/adv/v2/fullstats'
    LOAD_ADVERTS_STAT_WORDS_URL = 'https://advert-api.wildberries.ru/adv/v2/auto/stat-words'
    LOAD_KEYWORDS_STAT_URL = 'https://advert-api.wildberries.ru/adv/v0/stats/keywords'
    UPDATE_ADVERT_BIDS_URL = 'https://advert-api.wildberries.ru/adv/v0/bids'
    CREATE_WAREHOUSE_REMAINS_TASK_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains?groupByBrand={group_by_brand}&groupBySubject={group_by_subject}&groupBySa={group_by_sa}&groupByNm={group_by_nm}&groupByBarcode={group_by_barcode}&groupBySize={group_by_size}'
    CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/status'
    GET_WAREHOUSE_REMAINS_REPORT_URL = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/download'
    LOAD_FINANCIAL_REPORT_URL = 'https://statistics-api.wildberries.ru/api/v5/supplier/reportDetailByPeriod?dateFrom={date_from}&dateTo={date_to}'
    LOAD_INCOMES_URL = 'https://statistics-api.wildberries.ru/api/v1/supplier/incomes?dateFrom={date_from}'


class WBMerchantAPIClient:
    def __init__(self, seller: Seller, timeout: int = 20):
        self.seller = seller
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {seller.token}",
            "Content-Type": "application/json"
        })

    def _format_url(self, template: str, **kwargs) -> str:
        return template.format(**kwargs)

    def _request(
        self,
        method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        data_key: Optional[str] = None
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        try:
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get(data_key) if data_key else data
        except requests.RequestException as e:
            logging.error(f"[{self.seller.trade_mark}] API {method} request failed at {url}: {e}")
            notify_error(self.seller, f"API {method} request failed at {url}:\n{e}")
            return None

    def load_offices(self):
        return self._request('GET', MerchantAPIEndpoints.LOAD_WB_OFFICES_URL)

    def load_warehouses(self):
        return self._request('GET', MerchantAPIEndpoints.LOAD_WB_WAREHOUSES_URL)

    def load_seller_info(self):
        return self._request('GET', MerchantAPIEndpoints.LOAD_SELLER_INFO_URL)

    @sleep_and_retry
    @limits(calls=100, period=61)
    def load_seller_cards(self):
        payload = {"settings": {"cursor": {"limit": 100}, "filter": {"withPhoto": -1}}}
        return self._request('POST', MerchantAPIEndpoints.LOAD_SELLER_CARDS_URL, json_payload=payload)

    @sleep_and_retry
    @limits(calls=1, period=61)
    def load_incomes(self, last_updated: datetime):
        url = self._format_url(
            MerchantAPIEndpoints.LOAD_INCOMES_URL,
            date_from=last_updated.strftime("%Y-%m-%d")
        )
        return self._request('GET', url)

    @sleep_and_retry
    @limits(calls=1, period=61)
    def create_warehouse_task(self) -> Optional[str]:
        url = self._format_url(
            MerchantAPIEndpoints.CREATE_WAREHOUSE_REMAINS_TASK_URL,
            group_by_brand=True,
            group_by_subject=True,
            group_by_sa=True,
            group_by_nm=True,
            group_by_barcode=True,
            group_by_size=True
        )
        result = self._request('GET', url, data_key='data')
        return result.get('taskId') if result else None

    @sleep_and_retry
    @limits(calls=1, period=5)
    def check_warehouse_task_status(self, task_id: str) -> Optional[str]:
        url = self._format_url(MerchantAPIEndpoints.CHECK_WAREHOUSE_REMAINS_TASK_STATUS_URL, task_id=task_id)
        result = self._request('GET', url, data_key='data')
        return result.get('status') if result else None

    @sleep_and_retry
    @limits(calls=1, period=61)
    def load_warehouse_report(self, task_id: str):
        url = self._format_url(MerchantAPIEndpoints.GET_WAREHOUSE_REMAINS_REPORT_URL, task_id=task_id)
        return self._request('GET', url)

    @sleep_and_retry
    @limits(calls=3, period=61)
    def load_cards_stat(self, last_updated: datetime, cards: List[Card]):
        begin = datetime.combine(last_updated, time.min).strftime("%Y-%m-%d")
        end = datetime.now().strftime("%Y-%m-%d")
        nm_ids = [card.nm_id for card in cards]
        payload = {"nmIDs": nm_ids, "period": {"begin": begin, "end": end}, "aggregationLevel": "day"}
        return self._request('POST', MerchantAPIEndpoints.LOAD_CARD_STAT_DAILY_URL, json_payload=payload, data_key='data')

    @sleep_and_retry
    @limits(calls=1, period=61)
    def load_financial_report(self, date_from: datetime, date_to: datetime):
        url = self._format_url(
            MerchantAPIEndpoints.LOAD_FINANCIAL_REPORT_URL,
            date_from=date_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            date_to=date_to.strftime("%Y-%m-%dT%H:%M:%S.%f")
        )
        return self._request('GET', url)

    @sleep_and_retry
    @limits(calls=1, period=61)
    def load_orders(self, last_updated: datetime):
        params = {"dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), "flag": 0}
        return self._request('GET', MerchantAPIEndpoints.LOAD_ORDERS_URL, params=params)

    @sleep_and_retry
    @limits(calls=1, period=61)
    def load_sales(self, last_updated: datetime):
        params = {"dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), "flag": 0}
        return self._request('GET', MerchantAPIEndpoints.LOAD_SALES_URL, params=params)

    @sleep_and_retry
    @limits(calls=5, period=1)
    def load_adverts(self):
        count_data = self._request('GET', MerchantAPIEndpoints.LOAD_ADVERTS_COUNT_URL)
        if not count_data or 'adverts' not in count_data:
            return None
        advert_ids = {adv['advertId'] for grp in count_data['adverts'] for adv in grp['advert_list']}
        if not advert_ids:
            return None
        return self._request('POST', MerchantAPIEndpoints.LOAD_ADVERTS_INFO_URL, json_payload=list(advert_ids))

    @sleep_and_retry
    @limits(calls=5, period=1)
    def load_adverts_stat(self, adverts: List[Advert], last_updated: datetime):
        end = datetime.now().strftime("%Y-%m-%d")
        payload = [{"id": adv.advert_id, "interval": {"begin": last_updated.strftime("%Y-%m-%d"), "end": end}} for adv in adverts]
        return self._request('POST', MerchantAPIEndpoints.LOAD_ADVERTS_STAT_URL, json_payload=payload)

    @sleep_and_retry
    @limits(calls=4, period=1)
    def load_adverts_stat_words(self, advert: Advert):
        return self._request('GET', MerchantAPIEndpoints.LOAD_ADVERTS_STAT_WORDS_URL, params={"id": advert.advert_id})

    @sleep_and_retry
    @limits(calls=4, period=1)
    def load_keywords_stat(self, advert: Advert, date_from: datetime, date_to: datetime):
        params = {"advert_id": advert.advert_id, "from": date_from.strftime("%Y-%m-%d"), "to": date_to.strftime("%Y-%m-%d")}  # noqa
        return self._request('GET', MerchantAPIEndpoints.LOAD_KEYWORDS_STAT_URL, params=params)

    @sleep_and_retry
    @limits(calls=4, period=1)
    def update_advert_bids(self, data: List[Dict[str, Any]]):
        payload = {"bids": [
            {"advert_id": item["advert_id"], "nm_bids": [{"nm": b["nm_id"], "bid": b["bid"]} for b in item["bids"]]}
            for item in data
        ]}
        return self._request('PATCH', MerchantAPIEndpoints.UPDATE_ADVERT_BIDS_URL, json_payload=payload)
