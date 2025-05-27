from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from admin.db_router import get_session
from admin.services import get_my_seller

from web.routers.auth import get_current_user

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