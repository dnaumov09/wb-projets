import os
import requests
from datetime import datetime
from db.card import Card, save as save_card
from db.pipeline import Pipeline

from ratelimit import limits, sleep_and_retry

WB_MERCHANT_API_TOKEN = os.getenv('WB_MERCHANT_API_TOKEN')

headers = {
    "Authorization": f"Bearer {WB_MERCHANT_API_TOKEN}",
    "Content-Type": "application/json"
}

cards = []

ONE_MINUTE = 60
CALLS_COUNT = 3


@sleep_and_retry
@limits(calls=CALLS_COUNT, period=ONE_MINUTE)
def load_cards():
    url = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    payload = {
        "settings": {                      
            "cursor": {
              "limit": 100
            },
            "filter": {
              "withPhoto": -1
            }
          }
        }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    for card in data['cards']:
        save_card(Card(card['nmID'], card['imtID'], card['title'], card['vendorCode']))


@sleep_and_retry
@limits(calls=CALLS_COUNT, period=ONE_MINUTE)
def load_pipeline(begin: datetime, end: datetime, card: Card) -> Pipeline:
    end = end if end < datetime.now() else datetime.now()
    print(f"Начало дня: {begin} | Конец дня: {end} | {card.vendor_code}")


    url = 'https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail'
    payload = {
        "timezone": "Europe/Moscow",
        "nmIDs": [
            card.nm_id
        ],
        "period": {
            "begin": begin.strftime("%Y-%m-%d %H:%M:%S"),
            "end": end.strftime("%Y-%m-%d %H:%M:%S")
        },
        "page": 1
    }

    response = requests.post(url, headers=headers, json=payload)

    stat = response.json()['data']['cards'][0]['statistics']['selectedPeriod']

    return Pipeline(
        card,
        stat['begin'],
        stat['end'],
        stat['openCardCount'],
        stat['addToCartCount'],
        stat['ordersCount'],
        stat['ordersSumRub'],
        stat['buyoutsCount'],
        stat['buyoutsSumRub'],
        stat['cancelCount'],
        stat['cancelSumRub']
    )
