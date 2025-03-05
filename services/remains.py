import json
from db.warehouse import check_warehouse
from db.card import get_by_nm_id
from db.remains import save_or_update_remains
from db.warehouse_remains import check_warehouse_remains, update_warehouse_remains

def parse_remains_data(data):
    for item in data:
        card = get_by_nm_id(item.get('nmId'))
        if card is not None:
            warehouses = item.get('warehouses')
            remains = save_or_update_remains(
                    card=card, 
                    brand=item.get('brand'), 
                    subjectName=item.get('subjectName'), 
                    vendorCode=item.get('vendorCode'),
                    barcode=item.get('barcode'),
                    techSize=item.get('techSize'),
                    volume=item.get('volume'),
                    inWayToClient=item.get('inWayToClient'),
                    inWayFromClient=item.get('inWayFromClient'),
                    quantityWarehousesFull=item.get('quantityWarehousesFull')
                    )
            for warehouse in warehouses:
                warehouse_db = check_warehouse(warehouse.get('warehouseName'))
                warehouse_remains = check_warehouse_remains(warehouse_db.id, remains.nm_id)
                update_warehouse_remains(warehouse_remains, warehouse.get('quantity'))