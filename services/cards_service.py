import logging
from db.models.seller import Seller, get_sellers
from db.models.card import save_cards

from api import wb_merchant_api


def load_cards():
    for seller in get_sellers():
        if seller.id == 1:
            create_update_seller_cards(seller)


def create_update_seller_cards(seller: Seller):
    logging.info(f"Loading cards for seller {seller.name} ({seller.id})...")
    data = wb_merchant_api.load_seller_cards(seller)
    save_cards(data, seller)
    logging.info("Seller cards loaded")