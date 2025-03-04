from sqlalchemy import text
from db.base import session


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