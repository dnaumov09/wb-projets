import logging
from datetime import datetime
from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_sales
from db.models.settings import set_sales_last_updated
from db.models.sale import save_update_sales

def load_sales():
    for seller in get_sellers():
        if seller.id == 1:
            last_updated = datetime.now()
            data = wb_merchant_api.load_sales(last_updated, seller)

            if data is not None:
                updates = save_update_sales(data, seller)
                set_sales_last_updated(last_updated)
                logging.info(f"Sales saved")

                notify_updated_sales(updates)
