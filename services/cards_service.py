import logging
from db.models.seller import get_sellers
from db.models.card import save_cards

from api import wb_merchant_api
from db.models.seller import Seller


def load_cards():
    for seller in get_sellers():
        load_seller_cards(seller)


def load_seller_cards(seller: Seller):
    logging.info(f"[{seller.trade_mark}] Loading cards")
    data = wb_merchant_api.load_seller_cards(seller)
    if data:
        cards = save_cards(data, seller)
        # sheets_api.update_stat_cards_sheets(seller.google_drive_stat_spreadsheet_id, cards)
        logging.info(f"[{seller.trade_mark}] Cards saved {len(data)}")
