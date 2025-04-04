from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any

from enum import Enum
from typing import List, Tuple

from sqlalchemy import select, func, Integer, Float, String
from db.base import session


class Period(Enum):
    DAILY = 'day'
    WEEKLY = 'week'
    MONTHLY = 'month'


def get_stat_by_period(
    tvf_name: str,
    columns: List[Tuple[str, type]],
    period: Period,
    is_aggregated: bool = False
):
    # Dynamically call TVF and construct table
    table = getattr(func, tvf_name)(period.value).table_valued('period', 'nm_id', *[col for col, _ in columns]).alias('stat_table')

    if is_aggregated:
        aggregated_fields = [
            func.cast(func.sum(getattr(table.c, col)), col_type).label(col)
            for col, col_type in columns
        ]
        stmt = select(
            table.c.period,
            *aggregated_fields
        ).group_by(table.c.period).order_by(table.c.period)
    else:
        stmt = select(table)

    return session.execute(stmt).mappings().all()


def get_cards_stat_by_period(period: Period, is_aggregated: bool = False):
    columns = [
        ('open_card_count', Integer),
        ('add_to_cart_count', Integer),
        ('orders_count', Integer),
        ('orders_sum_rub', Float),
        ('buyouts_count', Integer),
        ('buyouts_sum_rub', Float),
        ('cancel_count', Integer),
        ('cancel_sum_rub', Float),
    ]
    return get_stat_by_period('get_cards_stat_by_period', columns, period, is_aggregated)


def get_orders_by_period(period: Period, is_aggregated: bool = False, is_cancelled: bool = False):
    columns = [
         ('count', Integer),
         ('total_price', Float),
         ('avg_total_price', Float),
         ('avg_spp', Float),
         ('finished_price', Float),
         ('avg_finished_price', Float),
         ('price_with_disc', Float),
         ('avg_price_with_disc', Float),
    ]
    return get_stat_by_period('get_orders_by_period', columns, period, is_aggregated)


def get_orders_cancelled_by_period(period: Period, is_aggregated: bool = False):
    columns = [
         ('count', Integer),
         ('total_price', Float),
         ('avg_total_price', Float),
         ('avg_spp', Float),
         ('finished_price', Float),
         ('avg_finished_price', Float),
         ('price_with_disc', Float),
         ('avg_price_with_disc', Float),
    ]
    return get_stat_by_period('get_orders_cancelled_by_period', columns, period, is_aggregated)


def get_sales_by_period(period: Period, is_aggregated: bool = False):
    columns = [
         ('count', Integer),
         ('total_price', Float),
         ('avg_total_price', Float),
         ('avg_discount_percent', Float),
         ('avg_spp', Float),
         ('for_pay', Float),
         ('avg_for_pay', Float),
         ('finished_price', Float),
         ('avg_finished_price', Float),
         ('price_with_disc', Float),
         ('avg_price_with_disc', Float)
    ]
    return get_stat_by_period('get_sales_by_period', columns, period, is_aggregated)


def get_pipeline_by_period(period: Period, is_aggregated: bool = False):
    columns = [
        ('vendor_code', String),
        ('open_card_count', Integer),
        ('add_to_cart_count', Integer),
        ('orders_count', Integer),
        ('orders_sum', Float),
        ('sales_count', Integer),
        ('sales_sum', Float),
        ('orders_cancelled_count', Integer),
        ('orders_cancelled_sum', Float),
        ('sales_returned_count', Integer),
        ('sales_returned_sum', Float),
    ]
    return get_stat_by_period('get_pipeline_by_period', columns, period, is_aggregated)


def get_date_ranges():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Day ranges
    yesterday = today - timedelta(days=1)
    
    # Week ranges (assuming weeks start on Monday)
    current_week_start = today - timedelta(days=today.weekday())
    last_week_start = current_week_start - timedelta(weeks=1)
    last_week_end = current_week_start - timedelta(days=1)

    # Month ranges
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - relativedelta(months=1)).replace(day=1)
    last_month_end = current_month_start - timedelta(days=1)
    
    return {
        'today': (today, today + timedelta(days=1)),
        'yesterday': (yesterday, today),
        'current_week': (current_week_start, today + timedelta(days=1)), #OR #'current_week': (current_week_start, current_week_start + timedelta(days=7)),
        'last_week': (last_week_start, last_week_end + timedelta(days=1)),
        'current_month': (current_month_start, today + timedelta(days=1)),
        'last_month': (last_month_start, last_month_end + timedelta(days=1)),
    }


def filter_pipeline_data(
    data: List[Dict[str, Any]],
    date_range: Tuple[datetime, datetime]
) -> List[Dict[str, Any]]:
    start_date, end_date = date_range
    return [
        row for row in data
        if start_date <= row['period'] < end_date
    ]


def get_pipeline_statistics(is_aggregated: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    date_ranges = get_date_ranges()
    
    # Load raw data from database
    daily_data = get_pipeline_by_period(Period.DAILY, is_aggregated)
    weekly_data = get_pipeline_by_period(Period.WEEKLY, is_aggregated)
    monthly_data = get_pipeline_by_period(Period.MONTHLY, is_aggregated)

    result = {}

    # Day-based ranges
    result['today'] = filter_pipeline_data(daily_data, date_ranges['today'])
    result['yesterday'] = filter_pipeline_data(daily_data, date_ranges['yesterday'])

    # Week-based ranges
    result['current_week'] = filter_pipeline_data(weekly_data, date_ranges['current_week'])
    result['last_week'] = filter_pipeline_data(weekly_data, date_ranges['last_week'])

    # Month-based ranges
    result['current_month'] = filter_pipeline_data(monthly_data, date_ranges['current_month'])
    result['last_month'] = filter_pipeline_data(monthly_data, date_ranges['last_month'])

    return result