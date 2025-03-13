import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from db.models.card_stat import save_update_card_stat
from db.models.settings import set_cards_stat_last_updated, get_cards_stat_last_updated

def load_cards_stat():
    for seller in get_sellers():
        if seller.id == 1:
            now = datetime.now()
            data = wb_merchant_api.load_cards_stat(get_cards_stat_last_updated(), seller)
            
            if data is not None:
                save_update_card_stat(data, now, seller)
                set_cards_stat_last_updated(now)
                logging.info(f"[{seller.trade_mark}] Cards stat saved")
