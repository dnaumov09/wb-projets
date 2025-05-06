import logging
from datetime import datetime

from db.model.seller import Seller
from db.model.card_stat import save_card_stat
from db.model.settings import get_seller_settings, save_settings
from db.model.card import get_cards

from utils.util import chunked

from wildberries.api import get_API

def load_cards_stat(seller: Seller):
    settings = get_seller_settings(seller)
    logging.info(f"[{seller.trade_mark}] Loading cards stat")
    now = datetime.now()
    seller_cards = get_cards(seller)
    if not seller_cards:
        pass
            
    data = []
    for cards_chunked in chunked(seller_cards, 20):
        data.extend(
            get_API(seller).seller_analytics.load_cards_stat(cards_chunked, settings.cards_stat_last_updated if settings.cards_stat_last_updated else now)
        )
    if data:
        saved_cards_stat = save_card_stat(data, now, seller)
        settings.cards_stat_last_updated = now
        save_settings(seller, settings)
        logging.info(f"[{seller.trade_mark}] Cards stat saved {len(saved_cards_stat)}")
                
