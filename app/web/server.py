import uvicorn
import threading
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from datetime import datetime, timedelta

from services.supplies_service import get_current_statuses

from utils.logging_settings import get_uvicorn_log_config


app = FastAPI()
TEMPLATES = Jinja2Templates(directory='app/web/templates')


def run_server():
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_config=get_uvicorn_log_config()
    )
    server = uvicorn.Server(config)
    server.run()


def start():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return TEMPLATES.TemplateResponse("404.html", {"request": request}, status_code=404)
    return await http_exception_handler(request, exc)


@app.get("/supplies", response_class=HTMLResponse)
def get_supplies(request: Request):
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

    return TEMPLATES.TemplateResponse("supplies_schedule.html", {
        "request": request,
        "schedule": schedule_data,
        "days": days
    })