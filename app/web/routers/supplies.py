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
    return templates.TemplateResponse("supplies_schedule.html", {"request": request})