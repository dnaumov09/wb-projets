from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy import and_

from admin.model import Seller
from admin.db_router import get_session

from db.model.sale import Sale, SaleStatus
from db.model.warehouse_remains import WarehouseRemains


def get_forecast(seller: Seller, forecast_days: int = 14, lead_time: int = 10):
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    session = get_session(seller)
    recent_sales = session.query(Sale).filter(and_(Sale.date >= seven_days_ago, Sale.status == SaleStatus.NEW)).all()

    # Группируем продажи по товару
    sales_by_key = defaultdict(list)
    for sale in recent_sales:
        key = (sale.nm_id, sale.warehouse_name)
        sales_by_key[key].append(sale.date)

    forecast_data = []
    remains = session.query(WarehouseRemains).all()

    for remain in remains:
        key = (remain.remains.nm_id, remain.warehouse.name)
        sales_dates = sales_by_key.get(key, [])
        last_week_sales_count = len(sales_dates)
        avg_daily_sales = last_week_sales_count / 7
        forecast_quantity = avg_daily_sales * forecast_days
        dayw_until_stockout = remain.quantity / avg_daily_sales if avg_daily_sales else None
        reorder_now = dayw_until_stockout <= lead_time if dayw_until_stockout else None
        reorder_quantity = avg_daily_sales * lead_time if avg_daily_sales else None
        
        forecast_data.append({
            "warehouse_id": remain.warehouse.id,
            "nm_id": remain.remains.card.nm_id,
            "quantity": remain.quantity,
            "last_week_sales_count": last_week_sales_count,
            "avg_daily_sales": avg_daily_sales,
            "needed_quantity": forecast_quantity,
            "days_until_stockout": dayw_until_stockout,
            "reorder_needed": reorder_now,
            "reorder_quantity": reorder_quantity
        })

    return sorted(forecast_data, key=lambda x: x["avg_daily_sales"], reverse=True)