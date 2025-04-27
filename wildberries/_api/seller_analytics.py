from typing import Optional, Dict, Any, List, Union
from datetime import datetime, time

from utils.util import rate_limited
from wildberries._api.base import BaseAPIClient, BaseAPIEndpoints

from db.model.card import Card


class SellerAnalyticsAPI(BaseAPIClient):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://seller-analytics-api.wildberries.ru/api"

        CREATE_WAREHOUSE_REMAINS_TASK = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "warehouse_remains")
        CHECK_WAREHOUSE_REMAINS_TASK_STATUS = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "warehouse_remains/tasks/{task_id}/status")
        DOWNLOAD_WAREHOUSE_REMAIN_REPORT = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "warehouse_remains/tasks/{task_id}/download")
        CARD_STAT_DAILY = BaseAPIEndpoints.url.__func__(_BASE_URL, "v2", "nm-report/detail/history")


    @rate_limited(calls=1, period=61)
    def create_warehouse_remains_task(self) -> int:
        params = {
            "groupByBrand": True,
            "groupBySubject": True,
            "groupBySa": True,
            "groupByNm": True,
            "groupByBarcode": True,
            "groupBySize": True
        }
        result = self.client.request('GET', SellerAnalyticsAPI.Endpoints.CREATE_WAREHOUSE_REMAINS_TASK, params=params, data_key='data')
        return result.get('taskId') if result else None
    

    @rate_limited(calls=1, period=5)
    def check_warehouse_remains_task_status(self, task_id: str) -> str:
        url = SellerAnalyticsAPI.Endpoints.CHECK_WAREHOUSE_REMAINS_TASK_STATUS.format(task_id=task_id)
        result = self.client.request('GET', url, data_key='data')
        return result.get('status') if result else None
    

    @rate_limited(calls=1, period=61)
    def download_warehouse_remains_report(self, task_id: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        url = SellerAnalyticsAPI.Endpoints.DOWNLOAD_WAREHOUSE_REMAIN_REPORT.format(task_id=task_id)
        return self.client.request('GET', url)
    

    @rate_limited(calls=3, period=61)
    def load_cards_stat(self, seller_cards: list[Card], last_updated: datetime) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        begin_date = datetime.combine(last_updated, time.min).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        nm_ids = [card.nm_id for card in seller_cards]
        payload = {
            "nmIDs": nm_ids,
            "period": {"begin": begin_date, "end": end_date},
            "aggregationLevel": "day"
        }
        return self.client.request('POST', SellerAnalyticsAPI.Endpoints.CARD_STAT_DAILY, json_payload=payload, data_key='data')
