import logging
from datetime import datetime, timedelta

from db.model.advert import AdvertType, Status, save_adverts, get_adverts_by_seller, Advert, get_active_adverts_by_seller, update_adverts
from db.model.adverts_stat import save_adverts_stat
from db.model.settings import get_seller_settings, save_settings
from db.model.advert_schedule import get_advert_schedule, AdvertSchedule, WeekDay

from clickhouse.model import keywords as ch_kw
from clickhouse.model import adverts as ch_ad

from admin.model import Seller

from wildberries.api import get_API, BaseAPIException, SellerAPI

from utils.util import chunked


def load_adverts(seller: Seller):
    try:
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
    except BaseAPIException as e:
        logging.error(f"Hidden API {e.method} ({e.url}) error {e.status_code}:\n{e.message}")


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
    try:
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
    except BaseAPIException as e:
        logging.error(f"Hidden API {e.method} ({e.url}) error {e.status_code}:\n{e.message}")


def load_keywords_stat(seller: Seller):
    try:
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
    except BaseAPIException as e:
        logging.error(f"Hidden API {e.method} ({e.url}) error {e.status_code}:\n{e.message}")



# ------ Автоматическое пополнение рекламных кампаний (расписание и бюджеты хранятся в Postgres)
MIN_TOPUP_AMOUNT = 1000

ONGOING_STATUSES = {Status.ONGOING}
STARTABLE_STATUSES = {Status.READY, Status.PAUSED}


def topup_adverts(seller: Seller):
    now = datetime.now()
    weekday = WeekDay(now.isoweekday() + 1) # так как запускается в scheduler в 23:55 прошедшего дня, то пополняем на след. день
    api = get_API(seller)
    adverts = _get_active_adverts(seller)
    balance = api.adverts.get_balance()
    
    for advert in adverts:
        today_schedule = get_advert_schedule(seller, advert.advert_id, weekday)
        
        if not _check_budget(today_schedule):
            continue

        toup_amount = max(today_schedule.max_daily_budget, MIN_TOPUP_AMOUNT)
        balance_from = _get_balance_from(balance, toup_amount)
        api.adverts.topup_advert(advert, toup_amount, balance_from)


def process_adverts(seller: Seller):
    now = datetime.now()
    weekday = WeekDay(now.isoweekday())
    api = get_API(seller)
    adverts = _get_active_adverts(seller)

    for advert in adverts:
        print(advert.name)
        today_schedule = get_advert_schedule(seller, advert.advert_id, weekday)
        if not _check_schedule_and_budget(today_schedule, now):
            if advert.status in ONGOING_STATUSES:
                api.adverts.stop_advert(advert)
                advert.status = Status.PAUSED
            continue # не в расписании или нет дневного бюджета

        if 'не пополн' in advert.name.lower():
            continue # не пополняем - остановлена
        
        if advert.status in STARTABLE_STATUSES:
            advert_budget = api.adverts.get_advert_budget(advert)
            if advert_budget and advert_budget['total']:
                api.adverts.start_advert(advert)
                advert.status = Status.ONGOING
    update_adverts(seller, adverts)


# обновляем кампании и получаем только активные 
def _get_active_adverts(seller: Seller) -> list[Advert]:
    load_adverts(seller)
    return get_active_adverts_by_seller(seller)


# проверяем расписание
def _check_schedule_and_budget(schedule: AdvertSchedule, now: datetime) -> bool:
    if not schedule:
        return False
    if now.hour not in {int(h.strip()) for h in schedule.hours.split(',') if h.strip().isdigit()}:
        return False
    if not schedule.weekday_active:
        return False

    return True


# проверяем есть ли доступный дневной бюджет
def _check_budget(schedule: AdvertSchedule):
    return schedule and schedule.max_daily_budget and schedule.max_daily_budget > 0


# получаем баланс по разным типам счетов
def _get_balance_from(balance, topup_amount):
    return (
        0 if balance.get('balance', 0) >= topup_amount else # счет
        1 if balance.get('net', 0) - balance.get('balance', 0) >= topup_amount else # баланс
        2 if balance.get('bonuses', 0) >= topup_amount else # бонусы
        None
    )
