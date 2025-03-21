import logging
from datetime import datetime
from api import wb_merchant_api
from db.model.seller import get_sellers
from db.model.advert import save_adverts, get_adverts_by_seller_id
from db.model.adverts_stat import save_adverts_stat
from db.model.settings import get_seller_settings, save_settings

def load_adverts():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_adverts_stat:
            logging.info(f"[{seller.trade_mark}] Loading adverts")
            data = wb_merchant_api.load_adverts(seller)
            if data:
                adverts = save_adverts(data, seller)
                logging.info(f"[{seller.trade_mark}] Adverts saved ({len(adverts)})")


#https://dev.wildberries.ru/openapi/analytics#tag/Statistika-po-prodvizheniyu/paths/~1adv~1v2~1fullstats/post
def load_adveerts_stat():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_adverts_stat:
            now = datetime.now()
            logging.info(f"[{seller.trade_mark}] Loading adverts stat")
            adverts = get_adverts_by_seller_id(seller)
            data = wb_merchant_api.load_adverts_stat(seller, adverts, settings.adverts_stat_last_updated if settings.adverts_stat_last_updated else now)
            if data:
                advert_stat, booster_stat = save_adverts_stat(data)
                settings.adverts_stat_last_updated = now
                save_settings(settings)
                logging.info(f"[{seller.trade_mark}] Adverts stat saved (adverts stat: {len(advert_stat)}, booster stat: {len(booster_stat)})")