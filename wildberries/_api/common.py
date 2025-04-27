from utils.util import rate_limited
from wildberries._api.base import BaseAPIClient, BaseAPIEndpoints


class CommonAPI(BaseAPIClient):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://common-api.wildberries.ru/api"

        SELLER_INFO = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "seller-info")


    def load_seller_info(self):
        return self.client.request('GET', CommonAPI.Endpoints.SELLER_INFO)