from wildberries._api.base import BaseAPIClient, BaseAPIEndpoints


class MarketplaceAPI(BaseAPIClient):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://marketplace-api.wildberries.ru/api"

        OFFICES = BaseAPIEndpoints.url.__func__(_BASE_URL, "v3", "offices")


    def load_wb_offices(self):
        return self.client.request('GET', MarketplaceAPI.Endpoints.OFFICES)