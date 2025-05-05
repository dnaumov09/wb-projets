import logging
from datetime import datetime, timedelta

from db.model.seller import Seller
from db.model.advert import AdvertType, save_adverts, get_adverts_by_seller
from db.model.adverts_stat import save_adverts_stat
from db.model.settings import get_seller_settings, save_settings

from clickhouse.model import keywords as ch_kw
from clickhouse.model import adverts as ch_ad

from wildberries.api import get_API

from utils.util import chunked


def load_adverts(seller: Seller):
    logging.info(f"[{seller.trade_mark}] Loading adverts")
    data = get_API(seller).adverts.load_adverts()

    if not data or 'adverts' not in data:
        return []
        
    advert_ids = [advert['advertId'] for group in data['adverts'] for advert in group['advert_list']]
    if not advert_ids:
        return []
        
    receaved_adverts = []
    for advert_ids_chunked in chunked(advert_ids, 50):
        receaved_adverts.extend(get_API(seller).adverts.load_adverts_info(advert_ids_chunked))
    
    if receaved_adverts:
        adverts = save_adverts(seller, receaved_adverts)
        ch_ad.save_adverts(seller, receaved_adverts)
        # save_advert_bids(data)
        logging.info(f"[{seller.trade_mark}] Adverts saved ({len(adverts)})")


def load_adverts_stat(seller: Seller):
    settings = get_seller_settings(seller)
    now = datetime.now()
    logging.info(f"[{seller.trade_mark}] Loading adverts stat")
    adverts = get_adverts_by_seller(seller)
    data = get_API(seller).adverts.load_adverts_stat(adverts, settings.adverts_stat_last_updated if settings.adverts_stat_last_updated else now)
    if data:
        advert_stat, booster_stat = save_adverts_stat(seller, data)
        ch_ad.save_advert_stat(seller, data)
        settings.adverts_stat_last_updated = now
        save_settings(seller, settings)
        logging.info(f"[{seller.trade_mark}] Adverts stat saved (adverts stat: {len(advert_stat)}, booster stat: {len(booster_stat)})")


def load_keywords(seller: Seller):
    logging.info(f"[{seller.trade_mark}] Loading keywords")
    adverts = get_adverts_by_seller(seller)

    clusters_to_save = []
    excluded_to_save = []

    for advert in adverts:
        if advert.advert_type != AdvertType.AUTOMATIC:
            continue
        data = get_API(seller).adverts.load_adverts_stat_words(advert)
            
        excluded_to_save.append({
            "advert_id": advert.advert_id,
            "keywords": data.get('excluded', []),
        })

        for cluster_data in data.get('clusters', []):
            clusters_to_save.append({
                "advert_id": advert.advert_id,
                "name": cluster_data.get('cluster'),
                "count": cluster_data.get('count'),
                "keywords": cluster_data.get('keywords', [])
            })
                    
    ch_kw.save_keywords_clusters(seller, clusters_to_save)
    ch_kw.save_keywords_excluded(seller, excluded_to_save)
            
    logging.info(f"[{seller.trade_mark}] Keywords saved")


def load_keywords_stat(seller: Seller):
    settings = get_seller_settings(seller)
    valid_types = {AdvertType.AUCTION, AdvertType.AUTOMATIC}

    logging.info(f"[{seller.trade_mark}] Loading keywords stat")

    adverts = get_adverts_by_seller(seller)
    adverts = [
        advert for advert in adverts
        if advert.advert_type in valid_types
    ]  
    
    now = datetime.now()
    date_from = settings.keywords_stat_last_updated
    data_to_save = []
    while date_from < now:
        date_to = min(date_from + timedelta(6), now)
        for advert in adverts:
            data = get_API(seller).adverts.load_keywords_stat(advert, date_from, date_to)
            if data:
                keywords = data.get('keywords', [])
                if keywords:
                    data_to_save.append({
                        'advert_id': advert.advert_id,
                        'stat': keywords
                    })
        date_from = date_to + timedelta(days=1)
        
    if not data_to_save:
        pass
    
    ch_kw.save_keywords_stat(seller, data_to_save)
    settings.keywords_stat_last_updated = now
    save_settings(seller, settings)
    logging.info(f"[{seller.trade_mark}] Keywords stat saved")










# ------------------- Параметры для расчёта -------------------
# TARGET_ROI = 3          # Целевой ROI (например, 3 = 300%)
# DEAD_ZONE = 0.01          # Зона нечувствительности: ±5% от целевого ROI
# MAX_ADJUST_STEP = 0.2     # Макс. изменение ставки за один шаг (±20%)
# MIN_BID = 10.0            # Минимальная допустимая ставка
# MAX_BID = 500.0           # Максимальная допустимая ставка
# DAYS_BACK = 7             # Берём статистику за последние 7 дней


# def get_current_bid(advert_id: int, nm_id: int):
#     return get_advert_bid(advert_id, nm_id)


# def update_bid(seller: Seller, advert_id: int, nm_id: int, current_bid: AdvertBid, new_bid: float):
#     logging.info(f"Updating bid: advert_id={advert_id}, nm_id={nm_id}, old_bid={current_bid.cpm}, new_bid={new_bid}")
#     # current_bid.cpm = new_bid
#     # update_advert_bid(current_bid)
#     # wb_merchant_api.update_advert_bids(seller, [{
#     #     'advert_id': advert_id, 
#     #     'bids': [{
#     #         'nm_id': nm_id,
#     #         'bid': int(round(new_bid))
#     #     }]
#     # }])


# def calculate_roi(revenue: float, cost: float) -> float:
#     """
#     ROI = (revenue - cost) / cost
#     Если cost <= 0, возвращаем 0.0, чтобы избежать деления на ноль.
#     """
#     if cost <= 0:
#         return 0.0
#     return (revenue - cost) / cost


# def calculate_drr(revenue: float, cost: float) -> float:
#     """
#     ДРР = cost / revenue
#     Если revenue <= 0, возвращаем 0.0, чтобы избежать деления на ноль.
#     """
#     if revenue <= 0:
#         return 0.0
#     return cost / revenue


# def update_bids(seller: Seller, days_back: int = DAYS_BACK):
#     """
#     Функция, которая:
#     1. Выгружает статистику за последние days_back дней.
#     2. Агегирует её по (advert_id, nm_id).
#     3. Считает ROAS.
#     4. Сравнивает с целевым ROAS и корректирует ставку.
#     5. Вызывает обновление ставки через update_bid.
#     """

#     now = datetime.now()
#     date_from = now - timedelta(days=days_back)

#     data = get_last_days_stat(seller, date_from)

#     for row in data:
#         advert_id = row.advert_id
#         nm_id = row.nm_id
#         total_cost = row.total_cost or 0.0
#         total_revenue = row.total_revenue or 0.0

#         # Считаем ROI
#         roi = calculate_roi(total_revenue, total_cost)
#         drr = calculate_drr(total_revenue, total_cost)
#         logging.info(f"ДРР = {drr}")

#         # Смотрим, на сколько % он отклоняется от TARGET_ROI
#         # Пример: если ROI = 1.5, а TARGET_ROI=2.0 => roi_diff = (1.5 - 2.0)/2.0 = -0.25 (-25%)
#         #         если ROI=3.0 => diff= (3.0-2.0)/2.0 = +0.5 (+50%)
#         if TARGET_ROI == 0:
#             roi_diff = 0.0
#         else:
#             roi_diff = (roi - TARGET_ROI) / TARGET_ROI

#         # Текущая ставка
#         current_bid = get_current_bid(advert_id, nm_id)

#         # Зона нечувствительности (если отклонение меньше ±DEAD_ZONE, ничего не делаем)
#         if abs(roi_diff) < DEAD_ZONE:
#             continue

#         # Коррекция ставки
#         # Если roi_diff>0 => ROI выше целевого => можем повысить ставку
#         # Если roi_diff<0 => ROI ниже целевого => снижаем ставку
#         # Но не более чем на ±MAX_ADJUST_STEP
#         if roi_diff > 0:
#             corr_ratio = min(roi_diff, MAX_ADJUST_STEP)
#         else:
#             corr_ratio = max(roi_diff, -MAX_ADJUST_STEP)

#         new_bid = current_bid.cpm * (1 + corr_ratio)

#         # Ограничиваем ставку заданными границами
#         new_bid = max(MIN_BID, min(new_bid, MAX_BID))

#         # Проверяем, есть ли смысл обновлять (изменение > 0.01)
#         if abs(new_bid - current_bid.cpm) > 0.01:
#             update_bid(seller, advert_id, nm_id, current_bid, new_bid)
