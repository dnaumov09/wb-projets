import time
import logging

from db.models.seller import Seller, get_sellers
from db.models.warehouse import get_warehouses
from db.models.remains import Remains, save_remains
from db.models.warehouse_remains import WarehouseRemains, save_warehouse_remains
from db.models.settings import get_seller_settings, save_settings

from api import wb_merchant_api


warehouses = get_warehouses()


def load_remains():
    for seller in get_sellers():
        settings = get_seller_settings(seller)
        if settings.load_remains:
            update_remains_data(seller)  


def update_remains_data(seller: Seller) -> list[Remains, WarehouseRemains]:
    logging.info(f"[{seller.trade_mark}] Sending remains report task")
    task_id = wb_merchant_api.create_warehouse_remains_task(seller)
    logging.info(f"[{seller.trade_mark}] Report task sent")
    
    logging.info(f"[{seller.trade_mark}] Checking task status ({task_id})")
    while wb_merchant_api.check_warehouse_remains_task_status(seller, task_id) != 'done':
        logging.info(f"[{seller.trade_mark}] Waiting for task to be done...")
        time.sleep(1)
    
    logging.info(f"[{seller.trade_mark}] Loading remains report")
    data = wb_merchant_api.load_warehouse_remains_report(seller, task_id)
    logging.info(f"[{seller.trade_mark}] Remains report receaved")

    remains = save_remains(data, seller)
    warehouse_remains = save_warehouse_remains(data, warehouses, remains)
    logging.info(f"[{seller.trade_mark}] Remains saved {len(warehouse_remains)}")