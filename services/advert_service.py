import logging
from api import wb_merchant_api
from db.models.seller import get_sellers
from db.models.adverts import save_adverts, get_adverts_by_seller_id

def load_adverts():
    for seller in get_sellers():
        if seller.id == 1:
            logging.info(f"[{seller.trade_mark}] Loading adverts")
            data = wb_merchant_api.load_adverts(seller)
            if data:
                save_adverts(data, seller)


#https://dev.wildberries.ru/openapi/analytics#tag/Statistika-po-prodvizheniyu/paths/~1adv~1v2~1fullstats/post
def load_adveerts_stat():
    for seller in get_sellers():
        if seller.id == 1:
            logging.info(f"[{seller.trade_mark}] Loading adverts stat")
            adverts = get_adverts_by_seller_id(seller)
            data = wb_merchant_api.load_adverts_stat(seller, adverts)
            if data:
                # save_adverts_stat()
                pass