import time
import logging

from db.model.seller import Seller
from db.model.warehouse import get_warehouses
from db.model.remains import save_remains
from db.model.warehouse_remains_snapshot import save_remains_snapshot
from db.model.card import get_seller_cards
from db.model.warehouse_remains import save_warehouse_remains, get_warehouse_remains_by_seller_id
from db.model.warehouse import check_warehouse
from db.util import camel_to_snake

from wildberries.api import get_API


warehouses = get_warehouses()


NOT_WAREHOUSES = {
    'В пути до получателей': 'in_way_to_client',
    'В пути возвраты на склад WB': 'in_way_from_client',
    'Всего находится на складах': 'quantity_warehouses_full'
}


def load_remains(seller: Seller):
    api = get_API(seller)
    
    logging.info(f"[{seller.trade_mark}] Sending remains report task")
    task_id = api.seller_analytics.create_warehouse_remains_task()
    logging.info(f"[{seller.trade_mark}] Report task sent")
    
    logging.info(f"[{seller.trade_mark}] Checking task status ({task_id})")
    while api.seller_analytics.check_warehouse_remains_task_status(task_id) != 'done':
        logging.info(f"[{seller.trade_mark}] Waiting for task to be done...")
        time.sleep(1)
    
    logging.info(f"[{seller.trade_mark}] Loading remains report")
    data = api.seller_analytics.download_warehouse_remains_report(task_id)
    logging.info(f"[{seller.trade_mark}] Remains report receaved")

    data = [
        {camel_to_snake(k): v for k, v in item.items()}
        for item in data
    ]

    seller_nm_ids = [r.nm_id for r in get_seller_cards(seller.id)]
    remains_keys = [ "nm_id", "brand", "subject_name", "vendor_code", "barcode", "tech_size", "volume" ]

    remains = []
    warehouse_remains = []
    for r in data:
        if r.get("nm_id") not in seller_nm_ids:
            continue
        remains_item = {key: r.get(key) for key in remains_keys}
        remains.append(remains_item)
        for wh in r.get('warehouses'):
            wh_name = wh.get('warehouseName')
            if wh_name in NOT_WAREHOUSES:
                key = NOT_WAREHOUSES[wh_name]
                remains_item[key] = remains_item.get(key, 0) + wh.get('quantity')
            else:
                warehouse_remains.append(
                    {
                        'remains_id': r.get('barcode'),
                        'warehouse_id': check_warehouse(wh_name).id,
                        'quantity': wh.get('quantity')
                    }
                )
        
    remains = save_remains(remains)
    warehouse_remains = save_warehouse_remains(warehouse_remains)
    logging.info(f"[{seller.trade_mark}] Remains saved {len(warehouse_remains)}")


def create_remains_snapshot(seller: Seller):
    logging.info(f"[{seller.trade_mark}] Creating remains snapshot")
    remains = get_warehouse_remains_by_seller_id(seller.id)
    save_remains_snapshot(remains)
    logging.info(f"[{seller.trade_mark}] Remains snapshot created")