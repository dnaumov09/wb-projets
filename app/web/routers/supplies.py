from datetime import datetime, timedelta

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from services.supplies_service import get_current_statuses
from web.security import model
from web.routers.auth import get_current_user


router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/supplies", response_class=HTMLResponse)
def get_supplies(request: Request, current_user: model.User = Depends(get_current_user)):
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

    return templates.TemplateResponse("supplies_schedule.html", {
        "request": request,
        "schedule": schedule_data,
        "days": days
    })