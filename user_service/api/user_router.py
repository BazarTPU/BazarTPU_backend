from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pathlib import Path

from starlette.responses import RedirectResponse

from user_service import templates, settings
from user_service.db.session import get_db
from user_service.api.models import User_sc
from user_service.api.actions.user import _get_user_by_id, _delete_user_by_id, _update_user_by_id, _create_new_user
from user_service.db.dals import UserDAL

user_router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "user_service/templates"))


@user_router.get("/user/profile", response_class=HTMLResponse)
async def get_profile_page(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    # First check if user is authenticated via cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)

    try:
        # Extract token from Bearer format
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        user_id = payload.get("user_id")

        if not email or not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)

        # Get user from database
        async with db.begin():
            user_dal = UserDAL(db)
            user = await user_dal.get_user_by_id(UUID(user_id))

            if not user:
                return RedirectResponse(url="/auth/login", status_code=302)

            user_photo = user.photo[0].file_path if user.photo else "/static/img/noLogoItem900.png"

            user_data = {
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email or "",
                "phone": user.phone_number or "",
                "telegram_id": user.telegram_id or "",
                "dormitory_id": user.dormitory.name if user.dormitory else "",
                "user_photo": user_photo
            }

            return templates.TemplateResponse(
                "profileInfo.html",
                {"request": request, "user": user_data}
            )
    except JWTError:
        return RedirectResponse(url="/auth/login", status_code=302)


@user_router.get("/user/profile/check")
async def check_auth(request: Request):
    # Check for token in cookies
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=302)

    return {"status": "authenticated"}
@user_router.post("/", response_model=User_sc)
async def create_user(body: User_sc, db: AsyncSession = Depends(get_db)):
    return await _create_new_user(body, db)

@user_router.delete("/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await _delete_user_by_id(user_id, db)


@user_router.get("/{user_id}", response_model=User_sc)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await _get_user_by_id(user_id, db)


@user_router.put("/{user_id}", response_model=User_sc)
async def update_user(user_id: UUID, body: User_sc, db: AsyncSession = Depends(get_db)):
    return await _update_user_by_id(user_id, body, db)