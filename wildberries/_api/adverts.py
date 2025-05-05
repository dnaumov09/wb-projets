from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from utils.util import rate_limited
from wildberries._api.base import BaseAPIClient, BaseAPIEndpoints

from db.model.advert import Advert

from utils.util import chunked


class AdvertAPI(BaseAPIClient):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://advert-api.wildberries.ru/adv"
        
        PROMOTION_COUNT = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "promotion/count")
        PROMOTION_ADVERTS = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "promotion/adverts")
        FULLSTAT = BaseAPIEndpoints.url.__func__(_BASE_URL, "v2", "fullstats")
        AUTO_STAT_WORDS = BaseAPIEndpoints.url.__func__(_BASE_URL, "v2", "auto/stat-words")
        STAT_KEYWORDS = BaseAPIEndpoints.url.__func__(_BASE_URL, "v0", "stats/keywords")
        BIDS = BaseAPIEndpoints.url.__func__(_BASE_URL, "v0", "bids")


    @rate_limited(calls=5, period=1)
    def load_adverts_info(self, advert_ids: list[int]):
        return self.request('POST', AdvertAPI.Endpoints.PROMOTION_ADVERTS, json_payload=list(advert_ids))
    

    @rate_limited(calls=5, period=1)
    def load_adverts(self) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        return self.request('GET', AdvertAPI.Endpoints.PROMOTION_COUNT)


    @rate_limited(calls=5, period=1)
    def load_adverts_stat(self, adverts: list[Advert], last_updated: datetime) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
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
        
        return self.request('POST', AdvertAPI.Endpoints.FULLSTAT, json_payload=payload)
    

    @rate_limited(calls=4, period=1)
    def load_adverts_stat_words(self, advert: Advert) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        params = {
            "id": advert.advert_id
        }

        return self.request('GET', AdvertAPI.Endpoints.AUTO_STAT_WORDS, params=params)


    @rate_limited(calls=4, period=1)
    def load_keywords_stat(self, advert: Advert, date_from: datetime, date_to: datetime) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        params = {
            "advert_id": advert.advert_id, 
            'from': date_from.strftime("%Y-%m-%d"), 
            'to': date_to.strftime("%Y-%m-%d")
        }
        
        return self.request('GET', AdvertAPI.Endpoints.STAT_KEYWORDS, params=params)


    @rate_limited(calls=4, period=1)
    def update_advert_bids(self, data) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
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
                
        return self.request('PATCH', AdvertAPI.Endpoints.BIDS, json_payload=payload)