import os

import httpx
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
from user_service.db.models import UserPhoto, Dormitory, User
from user_service.db.session import get_db
from user_service.api.models import User_sc
from user_service.api.actions.user import _get_user_by_id, _delete_user_by_id, _update_user_by_id, _create_new_user
from user_service.db.dals import UserDAL

user_router = APIRouter(tags=["User"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "user_service/templates"))

BASE_DIR = Path(__file__).parent.parent.parent  # Путь к корню проекта
AVATAR_UPLOAD_DIR = BASE_DIR / "user_service/static/uploads/avatars"
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)  # Создаем папку, если её нет


@user_router.get("/profile", response_class=HTMLResponse)
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

            # Получаем объявления пользователя - ИСПРАВЛЕНО
            user_ads = []
            try:
                print(f"Trying to fetch ads for user_id: {user_id}")
                async with httpx.AsyncClient() as client:
                    urls_to_try = [
                        # f"http://localhost:8001/ads/user/ads/{user_id}",
                        # f"http://ads-service:8001/ads/user/ads/{user_id}",
                        f"http://51.250.43.104/ads/user/ads/{user_id}"
                    ]

                    for url in urls_to_try:
                        try:
                            print(f"Trying URL: {url}")
                            response = await client.get(
                                url,
                                timeout=5.0,
                                headers={
                                    "Content-Type": "application/json",
                                    "Accept": "application/json"
                                }
                            )
                            print(f"Response status: {response.status_code}")

                            if response.status_code == 200:
                                user_ads = response.json()
                                print(f"Successfully fetched {len(user_ads)} ads")
                                break
                            else:
                                print(f"Failed with status {response.status_code}: {response.text}")
                        except Exception as e:
                            print(f"Error with URL {url}: {e}")
                            continue

            except Exception as e:
                print(f"Error fetching user ads: {e}")
                user_ads = []

            print(f"Final user_ads count: {len(user_ads)}")

            user_data = {
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email or "",
                "phone": user.phone_number or "",
                "telegram_id": user.telegram_id or "",
                "dormitories": [dorm.name for dorm in dormitories],
                "dormitory_id": user.dormitory.name if user.dormitory else "",
                "user_photo": user_photo,
                "user_ads": user_ads  # Передаем объявления пользователя
            }

            return templates.TemplateResponse(
                "profileInfo.html",
                {"request": request, "user": user_data}
            )
    except JWTError as e:
        print(f"JWT Error: {e}")
        return RedirectResponse(url="/auth/login", status_code=302)
    except Exception as e:
        print(f"Unexpected error in get_profile_page: {e}")
        return RedirectResponse(url="/auth/login", status_code=302)


@user_router.post("/profile/update", response_class=JSONResponse)
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


@user_router.post("/profile/upload-avatar", response_class=JSONResponse)
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

@user_router.get("/profile/check")
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

@user_router.post("/profile/update-additional-info", response_class=JSONResponse)
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

@user_router.get("/new-product")
async def redirect_to_new_product(request: Request):
    return RedirectResponse(url="/ads/newProduct")

@user_router.get("/ads/")
async def redirect_to_ads(request: Request):
    return RedirectResponse(url="/ads")


@user_router.get("/profile/json/{user_id}", response_class=JSONResponse)
async def get_user_profile_json(
        user_id: str,  # Изменено с UUID на str для более гибкой обработки
        db: AsyncSession = Depends(get_db)
):
    try:
        # Пробуем преобразовать в UUID, если это возможно
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    async with db.begin():
        user_dal = UserDAL(db)
        user = await user_dal.get_user_by_id(user_uuid)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_id": str(user.user_id),
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "",
            "phone": user.phone_number or "",
            "telegram_id": user.telegram_id or "",
            "user_photo": user.photo[0].file_path if user.photo and len(user.photo) > 0 else "/static/img/noLogoItem900.png"
        }

@user_router.get("/ads/{user_id}")
async def get_user_ads_proxy(user_id: str, request: Request):
    """Proxy для получения объявлений пользователя из ads service"""
    try:
        # Проверяем, что user_id - это UUID
        try:
            UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        async with httpx.AsyncClient() as client:
            # Передаем cookies из оригинального запроса
            cookies = request.cookies
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            # Пробуем разные варианты URL для подключения к ads service
            urls_to_try = [
                f"http://51.250.43.104/ads/user/ads/{user_id}",
                f"http://51.250.43.104/ads/user/ads/{user_id}",
                f"http://51.250.43.104/ads/user/ads/{user_id}"
            ]

            last_error = None
            for url in urls_to_try:
                try:
                    print(f"Trying to connect to: {url}")
                    response = await client.get(
                        url,
                        headers=headers,
                        cookies=cookies,
                        timeout=5.0
                    )

                    if response.status_code == 200:
                        print(f"Successfully connected to: {url}")
                        return response.json()
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        print(f"Failed with status {response.status_code} for {url}")

                except httpx.ConnectError as e:
                    last_error = f"Connection error: {str(e)}"
                    print(f"Connection error for {url}: {e}")
                    continue
                except httpx.TimeoutException as e:
                    last_error = f"Timeout error: {str(e)}"
                    print(f"Timeout error for {url}: {e}")
                    continue

            # Если все URL не сработали, возвращаем пустой список
            print(f"All connection attempts failed. Last error: {last_error}")
            return []

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in get_user_ads_proxy: {str(e)}")
        return []