import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from db.models.card_stat import save_update_card_stat
import db.models.settings as settings

def load_cards_stat():
    for seller in get_sellers():
        if seller.id == 1:
            last_updated = datetime.now()
            data = wb_merchant_api.load_cards_stat(last_updated, seller)
            
            if data is not None:
                save_update_card_stat(data, last_updated, seller)
                settings.set_cards_stat_last_updated(last_updated)
                logging.info("Cards stat saved")
