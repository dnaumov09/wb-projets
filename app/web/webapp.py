import uvicorn
import threading
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from fastapi.templating import Jinja2Templates


from web.routers import auth, errors, supplies
from web.api import data

from utils.logging_settings import get_uvicorn_log_config
from web.routers.auth import get_current_user

app = FastAPI()

app.include_router(auth.router)
app.include_router(errors.router)
app.include_router(supplies.router)
app.include_router(data.router)

app.mount("/static", StaticFiles(directory="app/web/templates/static"), name="static")
templates = Jinja2Templates(directory='app/web/templates')

def run_server():
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        # log_config=get_uvicorn_log_config()
    )
    server = uvicorn.Server(config)
    server.run()


def start():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()


@app.get("/")
async def home(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse("home.html", {"request": request})


ERROR_MESSAGES = {
    403: "Forbidden",
    404: "Page not found"
}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/login")
    message = ERROR_MESSAGES.get(exc.status_code, f"Undefined error")
    return templates.TemplateResponse("error.html", {"request": request, "message": message, "status_code": exc.status_code}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    status_code = 500
    return templates.TemplateResponse("error.html", {"request": request, "message": "Internal server error", "status_code": status_code}, status_code=status_code)