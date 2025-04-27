import logging
from db.model.seller import get_seller
from api import wb_merchant_api
from db.model.wb_office import save_wb_offices
from db.model.wb_warehouse import save_wb_warehouses


def load_wb_offices_and_warehouses():
    logging.info("Loading WB offices")
    
    data = wb_merchant_api.load_wb_offices(get_seller(1))
    updates = save_wb_offices(data)
    logging.info(f"WB offices saved {len(updates[0] + updates[1])}")
    
    data = wb_merchant_api.load_wb_warehouses(get_seller(1))
    updates = save_wb_warehouses(data)
    logging.info(f"WB warehouses saved {len(updates[0] + updates[1])}")
    