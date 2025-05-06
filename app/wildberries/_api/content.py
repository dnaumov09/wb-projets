from utils.util import rate_limited
from wildberries._api.base import BaseAPIClient, BaseAPIEndpoints


class ContentAPI(BaseAPIClient):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://content-api.wildberries.ru/content"

        CARDS_LIST = BaseAPIEndpoints.url.__func__(_BASE_URL, "v2", "get/cards/list")
    

    @rate_limited(calls=100, period=1)
    def load_seller_cards(self):
        payload = {
            "settings": {
                "cursor": {"limit": 100},
                "filter": {"withPhoto": -1}
            }
        }
        return self.request('POST', ContentAPI.Endpoints.CARDS_LIST, json_payload=payload)