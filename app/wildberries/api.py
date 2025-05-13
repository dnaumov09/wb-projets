from wildberries._api.adverts import AdvertAPI
from wildberries._api.common import CommonAPI
from wildberries._api.content import ContentAPI
from wildberries._api.marketplace import MarketplaceAPI
from wildberries._api.seller_analytics import SellerAnalyticsAPI
from wildberries._api.statistics import StatisticsAPI
from wildberries._api.supplies import SuppliesAPI
from wildberries._api.base import BaseAPIException

from admin.model import Seller


class SellerAPI():
    def __init__(self, seller: Seller):
        self.adverts = AdvertAPI(seller)
        self.common = CommonAPI(seller)
        self.content = ContentAPI(seller)
        self.marketplace = MarketplaceAPI(seller)
        self.seller_analytics = SellerAnalyticsAPI(seller)
        self.statistics = StatisticsAPI(seller)
        self.base = SuppliesAPI(seller)


_api_list = {}
def get_API(seller: Seller) -> SellerAPI:
        if seller.sid not in _api_list:
            _api_list[seller.sid] = SellerAPI(seller)

        return _api_list[seller.sid]