import logging
import requests

SELLER_INFO_URL = "https://common-api.wildberries.ru/api/v1/seller-info"

def get_seller_info(token: str):
    logging.info('☁️  Getting seller info')
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    response = requests.get(SELLER_INFO_URL, headers=headers)
    response.raise_for_status()
    logging.info('✅ Seller info receaved')
    return response.json()
