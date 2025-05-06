from typing import Optional, Dict, Any, List, Union

from datetime import datetime

from utils.util import rate_limited
from wildberries._api.base import BaseAPIClient, BaseAPIEndpoints

    
class StatisticsAPI(BaseAPIClient):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://statistics-api.wildberries.ru/api"

        ORDERS = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "supplier/orders")
        SALES = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "supplier/sales")
        INCOMES = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "supplier/incomes")
        FINANCIAL_REPORT = BaseAPIEndpoints.url.__func__(_BASE_URL, "v5", "supplier/reportDetailByPeriod")


    @rate_limited(calls=1, period=61)
    def load_orders(self, last_updated: datetime) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        params = {
            "dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), 
            "flag": 0
        }
        return self.request('GET', StatisticsAPI.Endpoints.ORDERS, params=params)
    

    @rate_limited(calls=1, period=61)
    def load_sales(self, last_updated: datetime) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        params = {
            "dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S"), 
            "flag": 0
        }
        return self.request('GET', StatisticsAPI.Endpoints.SALES, params=params)


    @rate_limited(calls=1, period=61)
    def load_incomes(self, last_updated: datetime) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        params = {
            "dateFrom": last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        }
        return self.request(method='GET', url=StatisticsAPI.Endpoints.INCOMES, params=params)


    @rate_limited(calls=1, period=61)
    def load_financial_report(self, date_from: datetime, date_to: datetime) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        params = {
            "dateFrom": date_from.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "dateTo": date_to.strftime("%Y-%m-%dT%H:%M:%S.%f")
        }
        return self.request(method='GET', url=StatisticsAPI.Endpoints.FINANCIAL_REPORT, params=params)