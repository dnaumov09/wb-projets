import requests
import logging
from typing import Optional, Dict, Any, List, Union, Literal

from db.model.seller import Seller
from bot.notification_service import notify_error


class BaseAPIException(Exception):
    def __init__(self, seller: Seller, method: str, url: str, message: str="Undefined exception"):
        super().__init__(f"[{seller.trade_mark}] API {method} request failed at {url}: {message}")


class BaseAPIClient:
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

    def request(
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
            raise BaseAPIException(seller=self.seller, method=method, url=url, message=e)
            # return None


class BaseAPIEndpoints:
    @classmethod
    def url(base_url: str, version: str, path: str) -> str:
        return f"{base_url}/{version}/{path}"
