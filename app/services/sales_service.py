import logging
from datetime import datetime, timedelta

from bot.notification_service import notify_updated_sales
from db.model.settings import get_seller_settings, save_settings
from db.model.sale import save_sales

from admin.model import Seller

from wildberries.api import get_API, BaseAPIException


def load_sales(seller: Seller, background: bool = False):
    try:
        settings = get_seller_settings(seller)
        logging.info(f"[{seller.trade_mark}] Loading sales")
        now = datetime.now()

        if background:
            date_from = now - timedelta(weeks=1)
        else:
            date_from = settings.sales_last_updated if settings.sales_last_updated else now
        data = get_API(seller).statistics.load_sales(date_from)

        if data:
            updates = save_sales(seller, data)
            settings.sales_last_updated = now
            save_settings(seller, settings)
            logging.info(f"[{seller.trade_mark}] Sales saved {len(updates[0] + updates[1])}")

            if not background:
                notify_updated_sales(updates[0] + updates[1])
    except BaseAPIException as e:
        logging.error(f"Hidden API {e.method} ({e.url}) error {e.status_code}:\n{e.message}")
