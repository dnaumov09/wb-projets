import logging

from api import sheets_api

from db.model.seller import get_sellers
from db.model.warehouse_remains import get_warehouse_remains_by_seller_id
from db.model.remains import get_remains_by_seller_id
from db.model.settings import get_seller_settings
from db import functions


def update_remains_data():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_remains:
            logging.info(f"[{seller.trade_mark}] Google Sheets remains updating...")
            remains = get_remains_by_seller_id(seller.id)
            sheets_api.update_remains_aggregated(seller, remains)

            warehouse_remains = get_warehouse_remains_by_seller_id(seller.id)
            sheets_api.update_remains_warehouses(seller, warehouse_remains)
            logging.info(f"[{seller.trade_mark}] Google Sheets remains updated")


def update_pipeline_data():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.update_pipeline_data:
            logging.info(f"[{seller.trade_mark}] Google Sheets pipeline updating...")
            pipeline = functions.get_pipeline_by_period(period=functions.Period.DAILY, is_aggregated=False)
            sheets_api.update_pipeline(seller, pipeline)
            logging.info(f"[{seller.trade_mark}] Google Sheets pipeline updated")


# def update_pipeline_detailed_data(): 
#     for seller in get_sellers():
#         if seller.id == 1:
#             logging.info(f"[{seller.trade_mark}] Google Sheets pipeline detailed updating...")
#             pipeline = functions.get_pipeline_by_period(functions.Period.DAILY, False)
#             grouped_pipeline = defaultdict(list)
#             cards = get_seller_cards(seller.id)

#             for item in pipeline:
#                 card = next(c for c in cards if c.nm_id == int(item.get('nm_id')))
#                 grouped_pipeline[card].append(item)
#             grouped_pipeline = dict(grouped_pipeline)

#             for card, pipeline in grouped_pipeline.items():
#                 sheets_api.update_card_pipeline(seller, pipeline, card)

#             logging.info(f"[{seller.trade_mark}] Google Sheets pipeline detailed updated")
