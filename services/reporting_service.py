from api import sheets_api

from db.models.seller import Seller
from db.models.warehouse_remains import get_warehouse_remains_by_seller_id
from db.models.remains import get_remains_by_seller_id


def update_remains_data(seller: Seller):
    remains = get_remains_by_seller_id(seller.id)
    sheets_api.update_remains_aggregated(seller, remains)

    warehouse_remains = get_warehouse_remains_by_seller_id(seller.id)
    sheets_api.update_remains_warehouses(seller, warehouse_remains)


def update_sales_data(seller: Seller):
    pass