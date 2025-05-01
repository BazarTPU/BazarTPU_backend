import uvicorn
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException, Form, status
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.log import echo_property
from sqlalchemy.orm import sessionmaker
from sqlalchemy.testing import future
from starlette.responses import RedirectResponse

import settings
from user_service.api.actions.user import _get_user_by_id, _update_user_by_id
from user_service.api.handlers import user_router
from user_service.api.login_handler import login_router, get_user_from_token
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from user_service.api.models import User_sc
from user_service import templates
from user_service.db.session import get_db

engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

app = FastAPI()
main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(login_router, prefix="/login", tags=["login"])
app.include_router(main_api_router)


@app.get("/profile", tags=["user"])
async def profile_page(
        request: Request,
        current_user: User_sc = Depends(get_user_from_token),
        db: AsyncSession = Depends(get_db),
        user_data = {
        "user_photo": None #пока нан
        }
):
    try:
        # получаем полные данные пользователя
        user = await _get_user_by_id(current_user.id, db)

        return templates.TemplateResponse("profileInfo.html", {
            "request": request,
            "user": {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "telegram_id": user.telegram_id,
                "dormitory": user.dormitory,
                "user_photo": user_data["user_photo"] or "/static/image/noLogoItem900.png"
            }
        })
    except HTTPException as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": e.detail,
            "status_code": e.status_code
        }, status_code=e.status_code)
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Внутренняя ошибка сервера",
            "status_code": 500
        }, status_code=500)


@app.post("/profile/update")
async def update_profile(
        request: Request,
        phone: str = Form(None),
        telegram: str = Form(None),
        dormitory: str = Form(None),
        current_user: User_sc = Depends(get_user_from_token),
        db: AsyncSession = Depends(get_db)
):
    try:
        update_data = User_sc(
            phone_number=phone,
            telegram_id=telegram,
            dormitory=dormitory
        )

        updated_user = await _update_user_by_id(current_user.id, update_data, db)

        return RedirectResponse(
            "/profile",
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/profile"}
        )

    except HTTPException as e:
        error_detail = str(e.detail)
        if "not found" in error_detail.lower():
            error_detail = "Пользователь не найден"
        return templates.TemplateResponse("profileInfo.html", {
            "request": request,
            "user": current_user.model_dump(),
            "error": error_detail
        }, status_code=e.status_code)

    except Exception as e:
        return templates.TemplateResponse("profileInfo.html", {
            "request": request,
            "user": current_user.model_dump(),
            "error": "Ошибка при обновлении профиля"
        }, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port = 8000)