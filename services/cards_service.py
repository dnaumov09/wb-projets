import logging
from db.models.seller import Seller, get_sellers
from db.models.card import save_cards

from api import wb_merchant_api


def load_cards():
    for seller in get_sellers():
        if seller.id == 1:
            updates = wb_merchant_api.load_seller_cards(seller)
            if updates is not None:
                save_cards(updates, seller)
                logging.info("Cards saved")