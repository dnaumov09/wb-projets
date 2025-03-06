from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_orders
from db.models.seller import get_seller

def load_orders():
    for seller in get_sellers():
        if seller.id == 1:
            updates = wb_merchant_api.load_orders(seller)
            notify_updated_orders(updates)
