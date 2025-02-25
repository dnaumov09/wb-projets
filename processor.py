import time
from datetime import datetime, time as dt_time, timedelta

from db.card import get_all as get_all_cards
from db.pipeline import save as save_pipeline
from db.settings import get_settings, save_settings
from api import wb_merchant_api


def load_stat():
    settings = get_settings()
    cards = get_all_cards()
    start_date = settings.last_updated
    end_date = datetime.now()
    current_date = start_date
    while current_date <= end_date:
        begin = datetime.combine(current_date, dt_time.min)
        end = datetime.combine(current_date, dt_time.max)
        for card in cards:
            save_pipeline(wb_merchant_api.load_pipeline(begin, end, card))
        current_date += timedelta(days=1)

    settings.last_updated = end_date
    save_settings(settings)