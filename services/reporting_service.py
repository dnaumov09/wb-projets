import logging
from api import sheets_api

from db.models.seller import Seller, get_sellers
from db.models.warehouse_remains import get_warehouse_remains_by_seller_id
from db.models.remains import get_remains_by_seller_id


def update_remains_data(seller: Seller):
    logging.info(f"Google Sheets remains updating for seller {seller.name}")
    remains = get_remains_by_seller_id(seller.id)
    sheets_api.update_remains_aggregated(seller, remains)

    warehouse_remains = get_warehouse_remains_by_seller_id(seller.id)
    sheets_api.update_remains_warehouses(seller, warehouse_remains)

    logging.info(f"Google Sheets remains updated")


def update_pipeline_data(seller: Seller):
    pass
