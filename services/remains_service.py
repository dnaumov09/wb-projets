import time
import logging

from db.models.seller import Seller, get_sellers, get_seller
from db.models.card import get_seller_cards
from db.models.warehouse import get_warehouses
from db.models.remains import Remains, save_remains
from db.models.warehouse_remains import WarehouseRemains, save_warehouse_remains, save_warehouse_remains_list, find_or_create_warehouse_remains

from api import wb_merchant_api


warehouses = get_warehouses()


def load_warehouses():
    logging.info(f"Loading warehouses...")
    data = wb_merchant_api.load_warehouses(get_seller(1))
    # save_warehouses(data)
    logging.info(f"Warehouses saved")


def load_remains():
    for seller in get_sellers():
        update_remains_data(seller)  


def update_remains_data(seller: Seller) -> list[Remains, WarehouseRemains]:
    logging.info(f"[{seller.trade_mark}] Loading remains...")
    task_id = wb_merchant_api.create_warehouse_remains_task(seller)
    logging.info(f"[{seller.trade_mark}] Report task created")
    
    while wb_merchant_api.check_warehouse_remains_task_status(seller, task_id) != 'done':
        logging.info(f"[{seller.trade_mark}] Waiting for task ({task_id}) to be done...")
        time.sleep(1)
    
    logging.info(f"[{seller.trade_mark}] Receiving remains data...")
    data = wb_merchant_api.load_warehouse_remains_report(seller, task_id)
    logging.info(f"[{seller.trade_mark}] Remains receaved")

    remains = save_remains(data, seller)
    warehouse_remains = save_warehouse_remains(data, warehouses, remains)
    
    #TODO говнокод
    # for item in data:
    #     nm_id = item.get('nmId')
    #     if nm_id not in seller_cards:
    #         continue

    #     card = seller_cards[nm_id]
    #     remains = save_remains(card, item)
       
    #     warehouses = item.get('warehouses')
    #     if not warehouses:
    #         continue
        
    #     for warehouse in warehouses:
    #         warehouse_db = check_warehouse(warehouse.get('warehouseName'))
    #         warehouse_remains = find_or_create_warehouse_remains(warehouse_db, remains, warehouse.get('quantity'))
    #         warehouse_remains_to_save.append(warehouse_remains)
    
    # save_warehouse_remains_list(warehouse_remains_to_save)
    logging.info(f"[{seller.trade_mark}] Remains saved")