import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_orders
from db.models.order import save_update_orders
from db.models.settings import set_orders_last_updated

def load_orders():
    for seller in get_sellers():
        if seller.id == 1:
            last_updated = datetime.now()
            data = wb_merchant_api.load_orders(last_updated, seller)
            
            if data is not None:
                updates = save_update_orders(data, seller)
                set_orders_last_updated(last_updated)
                logging.info(f"Orders saved")

                notify_updated_orders(updates)
