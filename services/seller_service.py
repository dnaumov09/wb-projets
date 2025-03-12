import logging
from db.models.seller import get_sellers_without_sid, update_seller_data
from api import wb_merchant_api, sheets_api
from services import cards_service


def check_and_create_sellers():
    sellers = get_sellers_without_sid()
    if not sellers:
        return
    logging.info("Found new sellers. Updating data and creating google drive folder...")
    for seller in sellers:
        logging.info(f"[{seller.trade_mark}] Loading seller info...")
        data = wb_merchant_api.load_seller_info(seller)
        seller_name = data.get('name')
        sellet_tradeMark = data.get('tradeMark')
        logging.info(f"[{seller.trade_mark}] Seller info receaved")
        logging.info(f"[{seller.trade_mark}] Creating google drive folder...")
        folder_id, stat_spreadsheet_id, remains_spreadsheet_id = sheets_api.create_seller_folder(sellet_tradeMark, seller)
        logging.info(f"[{seller.trade_mark}] Google drive folder created")
        update_seller_data(seller.token, data.get('sid'), seller_name, sellet_tradeMark, folder_id, stat_spreadsheet_id, remains_spreadsheet_id)
        logging.info(f"[{seller.trade_mark}] Seller data saved")
        cards_service.load_seller_cards(seller)
    logging.info("New sellers data updated")