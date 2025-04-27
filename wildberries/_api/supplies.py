from wildberries._api.base import BaseAPIClient, BaseAPIEndpoints


class SuppliesAPI(BaseAPIClient):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://supplies-api.wildberries.ru/api"

        WAREHOUSES = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "warehouses")


    def load_wb_warehouses(self):
        return self.request('GET', SuppliesAPI.Endpoints.WAREHOUSES)