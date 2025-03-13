
from api import wb_merchant_api
from db.models.seller import get_sellers
from db.models.adverts import save_adverts

def load_adverts():
    for seller in get_sellers():
        if seller.id == 1:
            data = wb_merchant_api.load_adverts(seller)
            save_adverts(data, seller)