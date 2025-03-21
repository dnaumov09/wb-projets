import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_sales
from db.models.settings import get_seller_settings, save_settings
from db.models.sale import save_sales

def load_sales():
    
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_sales:
            logging.info(f"[{seller.trade_mark}] Loading sales")
            now = datetime.now()
            data = wb_merchant_api.load_sales(settings.sales_last_updated if settings.sales_last_updated else now, seller)

            if data:
                updates = save_sales(data, seller)
                settings.sales_last_updated = now
                save_settings(settings)
                logging.info(f"[{seller.trade_mark}] Sales saved {len(data)}")

                notify_updated_sales(updates)
