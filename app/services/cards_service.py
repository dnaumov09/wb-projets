import logging

from db.model.card import save_cards

from admin.model import Seller

from wildberries.api import get_API, BaseAPIException


def load_cards(seller: Seller):
    try:
        logging.info(f"[{seller.trade_mark}] Loading cards")
        data = get_API(seller).content.load_seller_cards()
        cards = save_cards(seller, data)
        logging.info(f"[{seller.trade_mark}] Cards saved {len(cards[0] + cards[1])}")
    except BaseAPIException as e:
        logging.error(f"Hidden API {e.method} ({e.url}) error {e.status_code}:\n{e.message}")
