import logging
from datetime import datetime
from db.model.seller import get_sellers
from api import wb_merchant_api
from db.model.settings import get_seller_settings, save_settings

from db.model.realization import save_realizations

def load_finances():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_finances:
            logging.info(f"[{seller.trade_mark}] Loading financial report")
            date_to = datetime.now()
            data = wb_merchant_api.load_fincancial_report(settings.finances_last_updated if settings.finances_last_updated else date_to, date_to, seller)
            if not data:
                continue
            realizations = save_realizations(data, seller)
            settings.finances_last_updated = date_to
            save_settings(settings)
            logging.info(f"[{seller.trade_mark}] Financial report saved (rows: {len(realizations[0] + realizations[1])})")