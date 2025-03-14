import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_sales
from db.models.settings import set_sales_last_updated, get_sales_last_updated
from db.models.sale import save_sales

def load_sales():
    
    for seller in get_sellers():
        if seller.id == 1:
            logging.info(f"[{seller.trade_mark}] Loading sales")
            now = datetime.now()
            data = wb_merchant_api.load_sales(get_sales_last_updated(), seller)

            if data:
                updates = save_sales(data, seller)
                set_sales_last_updated(now)
                logging.info(f"[{seller.trade_mark}] Sales saved {len(data)}")

                notify_updated_sales(updates)
