from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/error/{code}")
async def show_error_page(request: Request, code: int):
    messages = {
        401: "Not authenticated (401)",
        403: "Forbidden (403)",
        404: "Page not found (404)",
        500: "Internal server error (500)",
    }
    message = messages.get(code, f"Error {code}")
    return templates.TemplateResponse("error.html", {"request": request, "message": message, "status_code": code}, status_code=code)
