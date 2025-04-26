import logging
from api import wb_merchant_api
from db.model.seller import Seller
from db.model.card import save_cards


def load_cards(seller: Seller):
    logging.info(f"[{seller.trade_mark}] Loading cards")
    data = wb_merchant_api.load_seller_cards(seller)
    if data:
        cards = save_cards(data, seller)
        logging.info(f"[{seller.trade_mark}] Cards saved {len(cards[0] + cards[1])}")
