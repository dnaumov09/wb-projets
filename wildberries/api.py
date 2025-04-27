from wildberries._api.base import BaseAPIClient as _BaseAPIClient

from wildberries._api.adverts import AdvertAPI as _AdvertAPI
from wildberries._api.common import CommonAPI as _CommonAPI
from wildberries._api.content import ContentAPI as _ContentAPI
from wildberries._api.marketplace import MarketplaceAPI as _MarketplaceAPI
from wildberries._api.seller_analytics import SellerAnalyticsAPI as _SellerAnalyticsAPI
from wildberries._api.statistics import StatisticsAPI as _StatisticsAPI
from wildberries._api.supplies import SuppliesAPI as _SuppliesAPI

from db.model.seller import Seller as _Seller


class SellerAPI():
    def __init__(self, seller: _Seller):
        client = _BaseAPIClient(seller)

        self.adverts = _AdvertAPI(client)
        self.common = _CommonAPI(client)
        self.content = _ContentAPI(client)
        self.marketplace = _MarketplaceAPI(client)
        self.seller_analytics = _SellerAnalyticsAPI(client)
        self.statistics = _StatisticsAPI(client)
        self.base = _SuppliesAPI(client)


_api_list = {}
def get_API(seller: _Seller) -> SellerAPI:
        if seller.id not in _api_list:
            _api_list[seller.id] = SellerAPI(seller)

        return _api_list[seller.id]