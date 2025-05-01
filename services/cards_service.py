import logging

from db.model.seller import Seller
from db.model.card import save_cards

from wildberries.api import get_API


def load_cards(seller: Seller):
    logging.info(f"[{seller.trade_mark}] Loading cards")
    data = get_API(seller).content.load_seller_cards()
    if data:
        cards = save_cards(seller, data)
        logging.info(f"[{seller.trade_mark}] Cards saved {len(cards[0] + cards[1])}")
