from wildberries._api.base import BaseAPI, BaseAPIEndpoints


class SuppliesAPI(BaseAPI):

    class Endpoints(BaseAPIEndpoints):

        _BASE_URL = "https://supplies-api.wildberries.ru/api"

        WAREHOUSES = BaseAPIEndpoints.url.__func__(_BASE_URL, "v1", "warehouses")


    def load_wb_warehouses(self):
        return self.client.request('GET', SuppliesAPI.Endpoints.WAREHOUSES)