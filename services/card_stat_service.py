import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from db.models.card_stat import save_card_stat
from db.models.settings import get_seller_settings, save_settings

def load_cards_stat():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_cards_stat:
            logging.info(f"[{seller.trade_mark}] Loading cards stat")
            now = datetime.now()
            data = wb_merchant_api.load_cards_stat(settings.cards_stat_last_updated if settings.cards_stat_last_updated else now, seller)
            
            if data:
                save_card_stat(data, now, seller)
                settings.cards_stat_last_updated = now
                save_settings(settings)
                logging.info(f"[{seller.trade_mark}] Cards stat saved {len(data)}")
                
