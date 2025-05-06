import requests
import json
from typing import Optional, Dict, Any, List, Union, Literal

from db.model.seller import Seller
from bot.notification_service import notify_error


class BaseAPIException(Exception):
    def __init__(self, seller: Seller, method: str, status_code: str, url: str, message: str):
        super().__init__(f"[{seller.trade_mark}] API {method} ({url}) error {status_code}:\n{message}")


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
            # notify_error(self.seller, f"API {method} request failed with code {e.response.status_code} at {url}:\n{e.response.json()}")
            raise BaseAPIException(
                seller=self.seller,
                method=method,
                status_code=e.response.status_code,
                url=url,
                message=json.dumps(e.response.json(), indent=4)
            )

class BaseAPIEndpoints:
    @classmethod
    def url(base_url: str, version: str, path: str) -> str:
        return f"{base_url}/{version}/{path}"
