from api import wb_merchant_api
from db.models.seller import get_sellers
from services.notification_service import notify_updated_orders

def load_cards_stat():
    for seller in get_sellers():
        if seller.id == 1:
            wb_merchant_api.load_cards_stat(seller)
