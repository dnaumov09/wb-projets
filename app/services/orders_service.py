import logging
from datetime import datetime, timedelta

from bot.notification_service import notify_updated_orders

from db.model.order import save_orders
from db.model.settings import get_seller_settings, save_settings

from admin.model import Seller

from wildberries.api import get_API, BaseAPIException

def load_orders(seller: Seller, background: bool = False):
    try:
        settings = get_seller_settings(seller)
        logging.info(f"[{seller.trade_mark}] Loading orders")
        now = datetime.now()
                
        if background:
            date_from = now - timedelta(weeks=1)
        else:
            date_from = settings.orders_last_updated if settings.orders_last_updated else now
        data = get_API(seller).statistics.load_orders(date_from)
                
        if data:
            updates = save_orders(seller, data)
            settings.orders_last_updated = now
            save_settings(seller, settings)
            logging.info(f"[{seller.trade_mark}] Orders saved {len(data)}")

            if not background:
                notify_updated_orders(updates[0] + updates[1])
    except BaseAPIException as e:
        logging.error(f"Hidden API {e.method} ({e.url}) error {e.status_code}:\n{e.message}")
