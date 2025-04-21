import logging
from datetime import datetime, timedelta
from api import wb_merchant_api

from bot.notification_service import notify_updated_sales
from db.model.settings import get_seller_settings, save_settings
from db.model.sale import save_sales
from db.model.seller import get_sellers

def load_sales(background: bool = False):
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_sales:
            logging.info(f"[{seller.trade_mark}] Loading sales")
            now = datetime.now()

            if background:
                date_from = now - timedelta(weeks=1)
            else:
                date_from = settings.orders_last_updated if settings.orders_last_updated else now
            data = wb_merchant_api.load_sales(date_from, seller)

            if data:
                updates = save_sales(data, seller)
                settings.sales_last_updated = now
                save_settings(settings)
                logging.info(f"[{seller.trade_mark}] Sales saved {len(updates[0] + updates[1])}")

                if not background:
                    notify_updated_sales(updates[0] + updates[1])
