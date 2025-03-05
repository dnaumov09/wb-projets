from sqlalchemy import text
from db.model import session
from datetime import datetime, time

from db.card_stat import save as save_card_stat
from db.card import get_all as get_all_cards


card_map = {c.nm_id: c for c in get_all_cards()}


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
    sql_query = text(f"select * from {function_name}('week', (SELECT DATE_TRUNC('week', CURRENT_DATE)::DATE))")
    return session.execute(sql_query).mappings().fetchall()


def get_last_week_stat(is_detailed: bool = False):
    function_name = "get_pipeline_by_period" if is_detailed else "get_pipeline_by_period_ttl" 
    sql_query = text(f"select * from {function_name}('week', (SELECT DATE_TRUNC('week', CURRENT_DATE  - INTERVAL '1 week')::DATE))")
    return session.execute(sql_query).mappings().fetchall()


def get_current_month_stat(is_detailed: bool = False):
    function_name = "get_pipeline_by_period" if is_detailed else "get_pipeline_by_period_ttl" 
    sql_query = text(f"select * from {function_name}('month', (SELECT DATE_TRUNC('month', CURRENT_DATE)::DATE))")
    return session.execute(sql_query).mappings().fetchall()


def get_last_month_stat(is_detailed: bool = False):
    function_name = "get_pipeline_by_period" if is_detailed else "get_pipeline_by_period_ttl" 
    sql_query = text(f"select * from {function_name}('month', (SELECT DATE_TRUNC('month', CURRENT_DATE  - INTERVAL '1 month')::DATE))")
    return session.execute(sql_query).mappings().fetchall()