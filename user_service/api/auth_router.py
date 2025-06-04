from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from user_service import settings
from user_service.db.session import get_db
from user_service.db.security import create_access_token
from pathlib import Path
from fastapi import HTTPException
from user_service.db.models import User, Dormitory
from user_service.api.actions.auth import authenticate_user, get_user_from_token


auth_router = APIRouter(prefix="/auth", tags=["Auth"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "user_service/templates"))


@auth_router.post("/token")
async def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.user_id)}
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        path="/",
        secure=False,
        samesite="lax"
    )

    if not user.phone_number or not user.dormitory_id:
        async with db.begin():
            stmt = select(Dormitory).order_by(Dormitory.name)
            result = await db.execute(stmt)
            dormitories = result.scalars().all()
            dormitory_names = [dorm.name for dorm in dormitories]

        return {"access_token": access_token, "token_type": "bearer",
                "redirect_url": "/auth/additional-info", "dormitories": dormitory_names}

    return {"access_token": access_token, "token_type": "bearer", "redirect_url": "/user/profile"}

@auth_router.get("/test_token")
async def test_jwt_token(current_user: User = Depends(get_user_from_token)):
    return {"succees": True, "user": current_user}

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("loginUser1.html", {"request": request})

@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}


@auth_router.get("/additional-info", response_class=HTMLResponse)
async def additional_info_page(request: Request, db: AsyncSession = Depends(get_db)):
    # Проверяем аутентификацию
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)

    try:
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")

        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)

        # Получаем список общежитий
        async with db.begin():
            stmt = select(Dormitory).order_by(Dormitory.name)
            result = await db.execute(stmt)
            dormitories = result.scalars().all()
            dormitory_names = [dorm.name for dorm in dormitories]

        return templates.TemplateResponse(
            "loginUser2.html",
            {"request": request, "dormitories": dormitory_names}
        )
    except JWTError:
        return RedirectResponse(url="/auth/login", status_code=302)