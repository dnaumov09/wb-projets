from enum import Enum
from typing import List, Tuple

from sqlalchemy import select, func, Integer, Float
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
        ('open_card_count', Integer),
        ('add_to_cart_count', Integer),
        ('orders_count', Integer),
        ('orders_sum', Float),
        ('sales_count', Integer),
        ('sales_sum', Float),
        ('orders_cancelled_count', Integer),
        ('orders_cancelled_sum', Float),
    ]
    return get_stat_by_period('get_pipeline_by_period', columns, period, is_aggregated)
