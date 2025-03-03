from sqlalchemy import text
from db.model import session
from datetime import datetime, time

from db.order import Order, save_update_orders
from db.sale import Sale, save_update_sales
from db.card_stat import save as save_card_stat
from db.card import get_all as get_all_cards
from db.settings import set_orders_last_updated, set_sales_last_updated, set_cards_stat_last_updated


card_map = {c.nm_id: c for c in get_all_cards()}


def save_orders(data, new_last_updated: datetime) -> list[Order]:
    updates = save_update_orders(data, card_map)
    set_orders_last_updated(new_last_updated)
    return updates


def save_sales(data, new_last_updated: datetime) -> list[Sale]:
    updates = save_update_sales(data, card_map)
    set_sales_last_updated(new_last_updated)
    return updates


# def save_orders(data, new_last_updated: datetime) -> list[Order]:
#     updates = []
#     for item in data:
#         card = card_map.get(item.get('nmId'))
#         order = save_order(
#             item.get('date'), item.get('lastChangeDate'), item.get('warehouseName'), item.get('warehouseType'),
#             item.get('countryName'), item.get('oblastOkrugName'), item.get('regionName'), item.get('supplierArticle'),
#             card, item.get('barcode'), item.get('category'), item.get('subject'), item.get('brand'),
#             item.get('techSize'), item.get('incomeID'), item.get('isSupply'), item.get('isRealization'),
#             item.get('totalPrice'), item.get('discountPercent'), item.get('spp'), item.get('finishedPrice'),
#             item.get('priceWithDisc'), item.get('isCancel'), item.get('cancelDate'), item.get('orderType'),
#             item.get('sticker'), item.get('gNumber'), item.get('srid')
#         )
#         updates.append(order)
#     set_orders_last_updated(new_last_updated)
#     return updates


# def save_sales(data, new_last_updated: datetime) -> list[Sale]:
#     updates = []
#     for item in data:
#         card = card_map.get(item.get('nmId'))
#         sale = save_sale(
#             item.get('date'), item.get('lastChangeDate'), item.get('warehouseName'), item.get('warehouseType'),
#             item.get('countryName'), item.get('oblastOkrugName'), item.get('regionName'), item.get('supplierArticle'),
#             card, item.get('barcode'), item.get('category'), item.get('subject'), item.get('brand'),
#             item.get('techSize'), item.get('incomeID'), item.get('isSupply'), item.get('isRealization'),
#             item.get('totalPrice'), item.get('discountPercent'), item.get('spp'), item.get('forPay'),
#             item.get('finishedPrice'), item.get('priceWithDisc'), item.get('saleID'), item.get('orderType'),
#             item.get('sticker'), item.get('gNumber'), item.get('srid'))
#         updates.append(sale)
#     set_sales_last_updated(new_last_updated)
#     return updates


def save_cards_stat(data, new_last_updated: datetime):
    for item in data:
        card = card_map.get(item.get('nmID'))
        history = item.get('history')
        for day in history:
            dt = datetime.strptime(day.get('dt'), "%Y-%m-%d")
            dt_end = datetime.combine(dt, time.max) if dt < datetime.combine(new_last_updated, time.min) else new_last_updated
            save_card_stat(
                dt,  dt_end, card, day.get('openCardCount'), day.get('addToCartCount'), day.get('ordersCount'),
                day.get('ordersSumRub'), day.get('buyoutsCount'), day.get('buyoutsSumRub'), day.get('cancelCount'), day.get('cancelSumRub')
                )
    
    set_cards_stat_last_updated(new_last_updated)


def get_today_stat(is_detailed: bool = False):
    function_name = "get_pipeline_by_period" if is_detailed else "get_pipeline_by_period_ttl" 
    sql_query = text(f"select * from {function_name}('day', (SELECT CURRENT_DATE))")
    return session.execute(sql_query).mappings().fetchall()


def get_yesterday_stat(is_detailed: bool = False):
    function_name = "get_pipeline_by_period" if is_detailed else "get_pipeline_by_period_ttl" 
    sql_query = text(f"select * from {function_name}('day', (SELECT CURRENT_DATE - INTERVAL '1 day'))")
    return session.execute(sql_query).mappings().fetchall()


def get_current_week_stat(is_detailed: bool = False):
    function_name = "get_pipeline_by_period" if is_detailed else "get_pipeline_by_period_ttl" 
    sql_query = text(f"select * from {function_name}('week', (SELECT DATE_TRUNC('day', CURRENT_DATE)::DATE))")
    return session.execute(sql_query).mappings().fetchall()


def get_current_month_stat(is_detailed: bool = False):
    function_name = "get_pipeline_by_period" if is_detailed else "get_pipeline_by_period_ttl" 
    sql_query = text(f"select * from {function_name}('month', (SELECT DATE_TRUNC('month', CURRENT_DATE)::DATE))")
    return session.execute(sql_query).mappings().fetchall()