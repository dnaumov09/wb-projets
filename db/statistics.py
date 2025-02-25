from sqlalchemy import text
from db.model import engine

def get_today_stat(is_detailed: bool = False):
    with engine.connect() as connection:
        from_view = 'daily_stat_detailed' if is_detailed else 'daily_stat'
        sql = text(f"SELECT * FROM {from_view} WHERE day_start = (SELECT MAX(day_start) FROM daily_stat)")
        result = connection.execute(sql)
        return result.mappings().all()
    

def get_yesterday_stat(is_detailed: bool = False):
    with engine.connect() as connection:
        from_view = 'daily_stat_detailed' if is_detailed else 'daily_stat'
        sql = text(f"SELECT * FROM {from_view} WHERE day_start = date_trunc('day', now() - interval '1 day')")
        result = connection.execute(sql)
        return result.mappings().all()
    

def get_current_week_stat(is_detailed: bool = False):
    with engine.connect() as connection:
        from_view = 'weekly_stat_detailed' if is_detailed else 'weekly_stat'
        sql = text(f"SELECT * FROM {from_view} WHERE week_start = (SELECT MAX(week_start) FROM weekly_stat)")
        result = connection.execute(sql)
        return result.mappings().all()
    

def get_current_month_stat(is_detailed: bool = False):
    with engine.connect() as connection:
        from_view = 'monthly_stat_detailed' if is_detailed else 'monthly_stat'
        sql = text(f"SELECT * FROM {from_view} WHERE month_start = (SELECT MAX(month_start) FROM monthly_stat)")
        result = connection.execute(sql)
        return result.mappings().all()
