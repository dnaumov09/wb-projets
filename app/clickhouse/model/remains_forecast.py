from admin.model import Seller
from admin.db_router import get_client

def save_remains_forecast(seller: Seller, forecast_data: dict):
    client = get_client(seller)

    rows = []
    for row in forecast_data:
        rows.append((
            int(row["warehouse_id"]),
            int(row["nm_id"]),
            int(row["quantity"]),
            int(row["last_week_sales_count"]),
            float(row["avg_daily_sales"]),
            float(row["needed_quantity"]),
            float(row["days_until_stockout"]) if row["days_until_stockout"] else None,
            bool(row["reorder_needed"]),
            float(row["reorder_quantity"]) if row["reorder_quantity"] else None
        ))

    client.execute(
        'INSERT INTO remains_forecast (warehouse_id, nm_id, quantity, last_week_sales_count, avg_daily_sales, needed_quantity, days_until_stockout, reorder_needed, reorder_quantity) VALUES', 
        rows
    )