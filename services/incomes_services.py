import logging
from datetime import datetime
from api import wb_merchant_api

from db.model.income import save_incomes
from db.model.seller import Seller
from db.model.settings import get_seller_settings, save_settings


def load_incomes(seller: Seller):
    settings = get_seller_settings(seller)
    logging.info(f"[{seller.trade_mark}] Loading incomes")
    now = datetime.now()
    data = wb_merchant_api.load_incomes(settings.incomes_last_updated if settings.incomes_last_updated else now, seller)

    if data:
        updates = save_incomes(data, seller)
        settings.incomes_last_updated = now
        save_settings(settings)
        logging.info(f"[{seller.trade_mark}] Incomes saved {len(updates[0] + updates[1])}")