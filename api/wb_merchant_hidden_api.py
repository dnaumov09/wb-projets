from __future__ import annotations
from functools import lru_cache
import os

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import requests


class MerchantHiddenAPIEndpoints:
    SUPPLIES_STATUS_URL = "https://seller-supply.wildberries.ru/ns/sm-supply/supply-manager/api/v1/supply/getAcceptanceCosts"


# ──────────────────────────────────────────────────────────────────────────────
# 1. Static configuration kept in one place
# ──────────────────────────────────────────────────────────────────────────────
@dataclass(slots=True, frozen=True)
class APIConfig:
    supplier_id: str
    wb_token: str
    validation_key: str


# ──────────────────────────────────────────────────────────────────────────────
# 2. Re-usable client
# ──────────────────────────────────────────────────────────────────────────────
class WBHiddenAPI:
    def __init__(
        self,
        cfg: APIConfig,
        session: Optional[requests.Session] = None,
        timeout: int | float = 10,
    ) -> None:
        self._cfg = cfg
        self._timeout = timeout
        self._s = session or requests.Session()

        self._s.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/135.0.0.0 Safari/537.36"
            ),
            "Content-Type": "application/json",
        })
        self._s.cookies.update({
                "x-supplier-id-external": cfg.supplier_id,
                "wbx-validation-key": cfg.validation_key,
                "WBTokenV3": cfg.wb_token,
            })

    def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._s.post(url, json=payload, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────
    def get_supplies(
        self,
        status_id: int = -1,
        search_by_id: Optional[int] = None,
    ) -> List[int]:
        payload = {
            "jsonrpc": "2.0",
            "id": "json-rpc_listSupplies",
            "params": {
                "statusId": status_id,
                "searchById": search_by_id,
            },
        }
        data = self._post(f"{SUPPLY_MANAGER_BASE_URL}/supply/listSupplies", payload)
        return data["result"]["data"] or []

    def get_acceptance_costs(
        self,
        date_from: datetime,
        date_to: datetime,
        preorder_id: Optional[int],
        supply_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": "json-rpc_getAcceptanceCosts",
            "params": {
                "dateFrom": date_from.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "dateTo": date_to.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "preorderID": preorder_id,
                "supplyId": supply_id,
            },
        }
        return self._post(MerchantHiddenAPIEndpoints.SUPPLIES_STATUS_URL, payload)
    

_client: WBHiddenAPI | None = None 
def _get_client() -> WBHiddenAPI:
    global _client  
    if _client is None:
        cfg = APIConfig(
            supplier_id=os.getenv('SUPPLIER_ID'),
            wb_token=os.getenv('WB_TOKEN'),
            validation_key=os.getenv('VALIDATION_KEY')
        )
        _client = WBHiddenAPI(cfg)
    return _client


def get_status():
    client = _get_client()
    date_from = datetime.now()
    date_to = date_from + timedelta(weeks=4) - timedelta(days=1)
    
    result = []
    try: 
        supplies = client.get_supplies()
        for supply in supplies:
            result.append({
                'supply': supply,
                'acceptance_costs': client.get_acceptance_costs(date_from, date_to, supply['preorderId'])['result']['costs']
            })
        return result
    finally:
        client._s.close()