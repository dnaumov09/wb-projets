import time
import logging

from db.model.seller import Seller, get_sellers
from db.model.warehouse import get_warehouses
from db.model.remains import Remains, save_remains, get_remains_by_seller_id
from db.model.warehouse_remains import WarehouseRemains, save_warehouse_remains
from db.model.settings import get_seller_settings
from db.model.warehouse import check_warehouse
from db.util import camel_to_snake

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

    data = [
        {camel_to_snake(k): v for k, v in item.items()}
        for item in data
    ]

    remains_nm_ids = [r.nm_id for r in get_remains_by_seller_id(seller.id)]
    remains_keys = [
        "nm_id", "brand", "subject_name", "vendor_code", "barcode",
        "tech_size", "volume", "in_way_to_client", "in_way_from_client", "quantity_warehouses_full"
    ]

    remains = []
    warehouse_remains = []
    for r in data:
        if r.get("nm_id") not in remains_nm_ids:
            continue

        remains.append({key: r.get(key) for key in remains_keys})
        for wh in r.get('warehouses'):
            warehouse_remains.append(
                {
                    'remains_id': r.get('barcode'),
                    'warehouse_id': check_warehouse(wh.get('warehouseName')).id,
                    'quantity': wh.get('quantity')
                }
            )
        

    remains = save_remains(remains)
    warehouse_remains = save_warehouse_remains(warehouse_remains)
    logging.info(f"[{seller.trade_mark}] Remains saved {len(warehouse_remains)}")