import logging
from datetime import datetime, timedelta

from db.model.settings import get_seller_settings, save_settings
from db.model.realization import save_realizations
from db.model.seller import Seller

from wildberries.api import get_API

from utils.util import chunked


def load_finances(seller: Seller):
    settings = get_seller_settings(seller)
    if settings.load_finances:
        logging.info(f"[{seller.trade_mark}] Loading financial report")
        last_monday = get_monday_000000000000(settings.finances_last_updated)
        last_sunday = get_last_sunday_235959999999()
        data = get_API(seller).statistics.load_financial_report(last_monday, last_sunday)
        if not data:
            pass
        
        realizations = []
        for chunk in chunked(data, 10000):
            realizations.append(save_realizations(chunk, seller))

        settings.finances_last_updated = datetime.now()
        save_settings(seller, settings)
        logging.info(f"[{seller.trade_mark}] Financial report saved (rows: {len(realizations[0] + realizations[1])})")


def get_last_sunday_235959999999():
    now = datetime.now()
    # isoweekday(): Monday=1 ... Sunday=7
    # If isoweekday() == 7, that means "today is Sunday,"
    # and we still want the "previous" Sunday, so offset = 7:
    offset = now.isoweekday() % 7 or 7
    
    # Step back to last Sunday
    last_sunday = now - timedelta(days=offset)
    
    # Replace the time with 23:59:59.999999
    last_sunday_235959 = last_sunday.replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    return last_sunday_235959


def get_monday_000000000000(date: datetime):
    # Monday is isoweekday() == 1, Tuesday == 2, ..., Sunday == 7
    # We subtract (isoweekday() - 1) days to go back to Monday.
    offset = date.isoweekday() - 1
    monday = date - timedelta(days=offset)
    # Set time to 00:00:00.000000
    monday_midnight = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return monday_midnight