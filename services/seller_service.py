import logging
from db.models.seller import get_sellers_without_sid, update_seller_data
from api import wb_merchant_api
from api.sheets_api import create_seller_folder

from services import cards_service


def check_and_create_sellers():
    sellers = get_sellers_without_sid()
    if not sellers:
        return
    logging.info("Found new sellers. Updating data and creating google drive folder...")
    for seller in sellers:
        logging.info(f"Loading seller info for ID {seller.id}")
        data = wb_merchant_api.load_seller_info(seller)
        seller_name = data.get('name')
        sellet_tradeMark = data.get('tradeMark')
        logging.info(f"Seller info receaved for {seller_name}")
        folder_id, stat_spreadsheet_id, remains_spreadsheet_id = create_seller_folder(sellet_tradeMark, seller)
        logging.info(f"Google drive folder created")
        update_seller_data(seller.token, data.get('sid'), seller_name, sellet_tradeMark, folder_id, stat_spreadsheet_id, remains_spreadsheet_id)
        logging.info(f"Seller data updated")
        cards_service.create_update_seller_cards(seller)