from fastapi import APIRouter, status, Request, Form, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt

from web.security import auth, crud, model

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory='app/web/templates')


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    scheme, _, param = token.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")

    try:
        payload = jwt.decode(param, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = crud.get_user(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# @router.get("/login")
# async def login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request, "error": None})


# @router.post("/logout")
# async def logout():
#     response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
#     response.delete_cookie(key="access_token")
#     return response


# @router.post("/login")
# async def login_for_access_token(
#     request: Request,
#     email: str = Form(...),
#     password: str = Form(...),
# ):
#     user = crud.get_user(email)
#     if not user or not auth.verify_password(password, user.password):
#         return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password"})
    
#     access_token = auth.create_access_token(data={"sub": user.email})
#     response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
#     response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
#     return response


# @router.get("/profile")
# async def read_users_me(request: Request, current_user: model.User = Depends(get_current_user)):
#     return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})
