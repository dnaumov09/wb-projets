import time
import logging

from db.models.seller import Seller, get_sellers
from db.models.card import get_seller_cards
from db.models.warehouse import check_warehouse
from db.models.remains import Remains, save_or_update_remains
from db.models.warehouse_remains import WarehouseRemains, save_warehouse_remains_list, find_or_create_warehouse_remains
from services import reporting_service

from api import wb_merchant_api


def load_remains():
    for seller in get_sellers():
        update_remains_data(seller)
        reporting_service.update_remains_data(seller)


def update_remains_data(seller: Seller) -> list[Remains, WarehouseRemains]:
    logging.info(f"[{seller.trade_mark}] Loading remains...")
    task_id = wb_merchant_api.create_warehouse_remains_task(seller)
    
    while wb_merchant_api.check_warehouse_remains_task_status(seller, task_id) != 'done':
        logging.info(f"[{seller.trade_mark}] Waiting for task ({task_id}) to be done...")
        time.sleep(1)
    
    data = wb_merchant_api.load_warehouse_remains_report(seller, task_id)
    logging.info(f"[{seller.trade_mark}] Remains receaved")

    warehouse_remains_to_save = []
    seller_cards = {card.nm_id: card for card in get_seller_cards(seller.id)}
    
    remains_list = []
    for item in data:
        nm_id = item.get('nmId')
        if nm_id not in seller_cards:
            continue

        card = seller_cards[nm_id]
        remains = save_or_update_remains(card, item)
        remains_list.append(remains)
       
        warehouses = item.get('warehouses')
        if not warehouses:
            continue
        
        for warehouse in warehouses:
            warehouse_db = check_warehouse(warehouse.get('warehouseName'))
            warehouse_remains = find_or_create_warehouse_remains(warehouse_db, remains, warehouse.get('quantity'))
            warehouse_remains_to_save.append(warehouse_remains)
    
    save_warehouse_remains_list(warehouse_remains_to_save)
    logging.info(f"[{seller.trade_mark}] Remains saved")
    return remains_list, warehouse_remains_to_save