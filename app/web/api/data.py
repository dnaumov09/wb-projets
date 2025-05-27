from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from admin.db_router import get_session
from admin.services import get_my_seller

from web.routers.auth import get_current_user
from services.supplies_service import get_current_statuses

router = APIRouter(prefix='/api')

@router.get("/orders")
async def get_chart_data(current_user = Depends(get_current_user)):
    session = get_session(get_my_seller())
    query = text("""
        SELECT period::date, sum(orders_count) as orders_count, sum(orders_sum) as orders_sum
        FROM get_pipeline_by_period('week')
        WHERE period >= current_date - interval '3 month'
        GROUP BY period
        ORDER BY period
    """)

    result = session.execute(query)
    rows = result.fetchall()

    labels = [row.period.isoformat() for row in rows]
    orders_count = [int(row.orders_count) if row.orders_count is not None else 0 for row in rows]
    orders_sum = [float(row.orders_sum) if row.orders_sum is not None else 0.0 for row in rows]

    data = {
        "labels": labels,
        "orders_count": orders_count,
        "orders_sum": orders_sum
    }
    return JSONResponse(content=data)


@router.get("/supplies")
async def get_supplies(current_user = Depends(get_current_user)):
    today = datetime.now().date()
    days = [(today + timedelta(days=i)).strftime('%d.%m') for i in range(14)]

    schedule_data = {}
    for entry in get_current_statuses():
        supply = entry['supply']
        warehouse_id = supply['warehouseId']
        warehouse_name = supply['warehouseName']
        is_real = supply['detailsQuantity'] > 1
        preorder_id = supply['preorderId']

        dates = {}
        for item in entry['acceptance_costs']:
            date_key = datetime.fromisoformat(item['date']).date().strftime('%d.%m')
            coefficient = item.get('coefficient')
            if coefficient is not None and coefficient > -1:
                dates[date_key] = {
                    'cost': item['cost'],
                    'coefficient': coefficient,
                }


        entry = schedule_data.get(warehouse_id)
        if not entry or (is_real and not entry['is_real']):
            schedule_data[warehouse_id] = {
                'warehouse_name': warehouse_name,
                'is_real': is_real,
                'preorders': {
                    preorder_id: dates
                }
            }
        elif is_real and entry['is_real']:
            entry['preorders'][preorder_id] = dates

    return JSONResponse(content={
        'days': days,
        'schedule': schedule_data
    })