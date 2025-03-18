from datetime import datetime, timedelta
from db.models.seller import get_sellers
from api import wb_merchant_api
from db.models.settings import get_finances_last_updated, set_finances_last_updated

from db.models.realization import save_realizations

def load_finances():
    for seller in get_sellers():
        if seller.id == 1:
            date_to = datetime.now()
            data = wb_merchant_api.load_fincancial_report(get_finances_last_updated(), date_to, seller)
            save_realizations(data)
            set_finances_last_updated(date_to)