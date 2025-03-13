import logging
from db.models.seller import get_sellers
from db.models.card import save_cards

from api import wb_merchant_api
from db.models.seller import Seller


def load_cards():
    for seller in get_sellers():
        load_seller_cards(seller)


def load_seller_cards(seller: Seller):
    updates = wb_merchant_api.load_seller_cards(seller)
    if updates is not None:
        cards = save_cards(updates, seller)
        # sheets_api.update_stat_cards_sheets(seller.google_drive_stat_spreadsheet_id, cards)
        logging.info(f"[{seller.trade_mark}] Cards saved")