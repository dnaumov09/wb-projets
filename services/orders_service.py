import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_orders
from db.models.order import save_update_orders
from db.models.settings import set_orders_last_updated, get_orders_last_updated

def load_orders():
    
    for seller in get_sellers():
        if seller.id == 1:
            now = datetime.now()
            data = wb_merchant_api.load_orders(get_orders_last_updated(), seller)
            
            if data is not None:
                updates = save_update_orders(data, seller)
                set_orders_last_updated(now)
                logging.info(f"[{seller.trade_mark}] Orders saved")

                notify_updated_orders(updates)
