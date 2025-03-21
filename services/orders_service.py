import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_orders
from db.models.order import save_orders
from db.models.settings import get_seller_settings, save_settings

def load_orders():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_orders:
            logging.info(f"[{seller.trade_mark}] Loading orders")
            now = datetime.now()
            data = wb_merchant_api.load_orders(settings.orders_last_updated if settings.orders_last_updated else now, seller)
            
            if data:
                updates = save_orders(data, seller)
                settings.orders_last_updated = now
                save_settings(settings)
                logging.info(f"[{seller.trade_mark}] Orders saved {len(data)}")

                notify_updated_orders(updates)
