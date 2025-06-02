import logging
from datetime import datetime

from db.model.settings import get_seller_settings, save_settings
from db.model.card import get_cards
from clickhouse.model import cards as ch_cards

from admin.model import Seller

from utils.util import chunked

from wildberries.api import get_API, BaseAPIException

def load_cards_stat(seller: Seller):
    try:
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
            # saved_cards_stat = save_card_stat(data, now, seller)
            ch_cards.save_cards_stat_hourly(seller, data, now.date(), now.hour - 1)
            ch_cards.save_cards_stat(seller, data)
            settings.cards_stat_last_updated = now
            save_settings(seller, settings)
            logging.info(f"[{seller.trade_mark}] Cards stat saved")
    except BaseAPIException as e:
        logging.error(f"Hidden API {e.method} ({e.url}) error {e.status_code}:\n{e.message}")
                
