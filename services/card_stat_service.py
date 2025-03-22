import logging
from datetime import datetime
from api import wb_merchant_api
from db.model.seller import get_sellers
from db.model.card_stat import save_card_stat
from db.model.settings import get_seller_settings, save_settings
from db.model.card import get_seller_cards

def load_cards_stat():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_cards_stat:
            logging.info(f"[{seller.trade_mark}] Loading cards stat")
            now = datetime.now()
            seller_cards = get_seller_cards(seller.id)
            if not seller_cards:
                continue
            
            data = wb_merchant_api.load_cards_stat(settings.cards_stat_last_updated if settings.cards_stat_last_updated else now, seller, seller_cards)
            if data:
                saved_cards_stat = save_card_stat(data, now, seller)
                settings.cards_stat_last_updated = now
                save_settings(settings)
                logging.info(f"[{seller.trade_mark}] Cards stat saved {len(saved_cards_stat)}")
                
