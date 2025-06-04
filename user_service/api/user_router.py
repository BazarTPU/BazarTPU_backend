import os

from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from pathlib import Path

from sqlmodel import select
from starlette.responses import RedirectResponse, JSONResponse

from user_service import templates, settings
from user_service.db.models import UserPhoto, Dormitory
from user_service.db.session import get_db
from user_service.api.models import User_sc
from user_service.api.actions.user import _get_user_by_id, _delete_user_by_id, _update_user_by_id, _create_new_user
from user_service.db.dals import UserDAL

user_router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "user_service/templates"))

BASE_DIR = Path(__file__).parent.parent.parent  # Путь к корню проекта
AVATAR_UPLOAD_DIR = BASE_DIR / "user_service/static/uploads/avatars"
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)  # Создаем папку, если её нет

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
            dormitories_query = select(Dormitory).order_by(Dormitory.name)
            dormitories_result = await db.execute(dormitories_query)
            dormitories = dormitories_result.scalars().all()

            if not user:
                return RedirectResponse(url="/auth/login", status_code=302)

            user_photo = user.photo[0].file_path if user.photo else "/static/img/noLogoItem900.png"

            user_data = {
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email or "",
                "phone": user.phone_number or "",
                "telegram_id": user.telegram_id or "",
                "dormitories": [dorm.name for dorm in dormitories],
                "dormitory_id": user.dormitory.name if user.dormitory else "",
                "user_photo": user_photo
            }

            return templates.TemplateResponse(
                "profileInfo.html",
                {"request": request, "user": user_data}
            )
    except JWTError:
        return RedirectResponse(url="/auth/login", status_code=302)


@user_router.post("/user/profile/update", response_class=JSONResponse)
async def update_profile(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    try:
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        user_id = payload.get("user_id")

        if not email or not user_id:
            return JSONResponse(content={"error": "Invalid token"}, status_code=401)

        form_data = await request.json()
        phone_number = form_data.get("phone_number")
        telegram_id = form_data.get("telegram_id")
        dormitory_name = form_data.get("dormitory_id")

        dorm_id = None
        if dormitory_name and dormitory_name != "Выберите номер общежития":
            async with db.begin():
                query = select(Dormitory).where(Dormitory.name == dormitory_name)
                result = await db.execute(query)
                dormitory = result.scalar_one_or_none()
                if dormitory:
                    dorm_id = dormitory.id
                else:
                    return JSONResponse(
                        content={"error": "Указанное общежитие не найдено"},
                        status_code=400
                    )

        async with db.begin():
            user_dal = UserDAL(db)
            updated_user = await user_dal.update_user_by_id(
                user_id=UUID(user_id),
                phone_number=phone_number,
                telegram_id=telegram_id,
                dormitory_id=dorm_id
            )

            if not updated_user:
                return JSONResponse(content={"error": "Failed to update user"}, status_code=400)

            # Get updated user with dormitory info
            user = await user_dal.get_user_by_id(UUID(user_id))
            dormitory_name = user.dormitory.name if user.dormitory else ""

            return JSONResponse(content={
                "success": True,
                "message": "Профиль успешно обновлен",
                "user": {
                    "phone": phone_number,
                    "telegram_id": telegram_id,
                    "dormitory_id": dormitory_name
                }
            })
    except JWTError:
        return JSONResponse(content={"error": "Invalid token"}, status_code=401)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@user_router.post("/user/profile/upload-avatar", response_class=JSONResponse)
async def upload_avatar(
        request: Request,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    try:
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            return JSONResponse(content={"error": "Invalid token"}, status_code=401)

        # Проверяем тип файла
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            return JSONResponse(
                content={"error": "Invalid file type. Only images allowed."},
                status_code=400
            )

        # Генерируем уникальное имя файла
        filename = f"{uuid4()}{file_ext}"
        absolute_path = AVATAR_UPLOAD_DIR / filename  # Полный путь к файлу
        relative_path = f"/static/uploads/avatars/{filename}"  # Путь для URL

        # Сохраняем файл
        contents = await file.read()
        with open(absolute_path, "wb") as f:
            f.write(contents)

        # Обновляем запись в БД
        async with db.begin():
            user_dal = UserDAL(db)
            user = await user_dal.get_user_by_id(UUID(user_id))

            # Удаляем старый аватар (если есть)
            if user.photo:
                for old_photo in user.photo:
                    old_path = BASE_DIR / old_photo.file_path.lstrip("/")
                    try:
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception as e:
                        print(f"Error deleting old avatar: {e}")

                # Удаляем записи из БД
                await db.execute(delete(UserPhoto).where(UserPhoto.user_id == UUID(user_id)))

            # Добавляем новую запись
            new_photo = UserPhoto(
                user_id=UUID(user_id),
                file_path=relative_path
            )
            db.add(new_photo)

        return JSONResponse(content={
            "success": True,
            "message": "Аватар успешно загружен",
            "file_path": relative_path
        })

    except JWTError:
        return JSONResponse(content={"error": "Invalid token"}, status_code=401)
    except Exception as e:
        print(f"Avatar upload error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

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

@user_router.post("/user/profile/update-additional-info", response_class=JSONResponse)
async def update_additional_info(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    try:
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")

        if not user_id:
            return JSONResponse(content={"error": "Invalid token"}, status_code=401)

        form_data = await request.json()
        phone_number = form_data.get("phone_number")
        dormitory_name = form_data.get("dormitory_id")

        dorm_id = None
        if dormitory_name:
            async with db.begin():
                query = select(Dormitory).where(Dormitory.name == dormitory_name)
                result = await db.execute(query)
                dormitory = result.scalar_one_or_none()
                if dormitory:
                    dorm_id = dormitory.id

        async with db.begin():
            user_dal = UserDAL(db)
            updated_user = await user_dal.update_user_by_id(
                user_id=UUID(user_id),
                phone_number=phone_number,
                dormitory_id=dorm_id
            )

            if not updated_user:
                return JSONResponse(content={"error": "Failed to update user"}, status_code=400)

            return JSONResponse(content={
                "success": True,
                "message": "Данные успешно сохранены"
            })
    except JWTError:
        return JSONResponse(content={"error": "Invalid token"}, status_code=401)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
