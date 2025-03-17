import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from db.models.advert import save_adverts, get_adverts_by_seller_id
from db.models.adverts_stat import save_adverts_stat
from db.models.settings import get_adverts_stat_last_updated, set_adverts_stat_last_updated

def load_adverts():
    for seller in get_sellers():
        if seller.id == 1:
            logging.info(f"[{seller.trade_mark}] Loading adverts")
            data = wb_merchant_api.load_adverts(seller)
            if data:
                adverts = save_adverts(data, seller)
                logging.info(f"[{seller.trade_mark}] Adverts saved ({len(adverts)})")


#https://dev.wildberries.ru/openapi/analytics#tag/Statistika-po-prodvizheniyu/paths/~1adv~1v2~1fullstats/post
def load_adveerts_stat():
    for seller in get_sellers():
        if seller.id == 1:
            now = datetime.now()
            logging.info(f"[{seller.trade_mark}] Loading adverts stat")
            adverts = get_adverts_by_seller_id(seller)
            data = wb_merchant_api.load_adverts_stat(seller, adverts, get_adverts_stat_last_updated())
            if data:
                advert_stat, booster_stat = save_adverts_stat(data)
                set_adverts_stat_last_updated(now)
                logging.info(f"[{seller.trade_mark}] Adverts stat saved (adverts stat: {len(advert_stat)}, booster stat: {len(booster_stat)})")