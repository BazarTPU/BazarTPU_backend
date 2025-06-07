from idlelib.query import Query
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Body, Request, UploadFile, File, Form, Query, HTTPException
from fastapi.params import Path
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from watchfiles import awatch
from typing import List
from sqlalchemy import select
from fastapi.responses import RedirectResponse

from ads_service.db.session import get_db
from ads_service.api.models import Ads_sc, Category_sc, Dormitory_sc, AdUpdate_sc
from ads_service.api.actions.ads import _create_new_ad, _create_new_category, _create_new_dormitory, _delete_dormitory, \
    _delete_ad, _delete_category, _update_ad, _get_all_ads, _get_search_ads, _get_ads_by_category, _get_one_ad
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from user_service import settings
templates = Jinja2Templates(directory='templates')


ads_router = APIRouter()


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@ads_router.post("/create_new_ad", response_model=Ads_sc)
async def create_new_ad(
        request: Request,
        category_id: int = Form(...),
        title: str = Form(...),
        description: str = Form(...),
        address: str = Form(None),
        dormitory_id: int = Form(None),
        price: float = Form(...),
        photos: list[UploadFile] = File(None),
        db: AsyncSession = Depends(get_db),
        user_id: str = Depends(get_current_user)
):
    # Сохраняем фото на диск и собираем пути
    photo_paths = []
    if photos:
        import os
        upload_dir = "ads_service/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        for photo in photos:
            file_location = os.path.join(upload_dir, photo.filename)
            with open(file_location, "wb") as f:
                f.write(await photo.read())
            photo_paths.append(f"/ads/static/uploads/{photo.filename}")

    # Собираем данные для модели
    ad_data = Ads_sc(
        user_id=user_id,
        category_id=category_id,
        title=title,
        description=description,
        address=address,
        dormitory_id=dormitory_id,
        price=price,
        photos=photo_paths
    )
    return await _create_new_ad(ad_data, db)


@ads_router.post("/categories", response_model=Category_sc)
async def create_category(body: Category_sc, db: AsyncSession = Depends(get_db)):
    return await _create_new_category(body, db)


@ads_router.post("/dormitories", response_model=Dormitory_sc)
async def create_dormitory(body: Dormitory_sc, db: AsyncSession = Depends(get_db)):
    print("BODY TYPE:", type(body), body)
    return await _create_new_dormitory(body, db)


@ads_router.delete("/dormitories/{dormitory_id}", status_code=204)
async def delete_dormitory(dormitory_id: int, db: AsyncSession = Depends(get_db)):
    return await _delete_dormitory(dormitory_id, db)


@ads_router.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    return await _delete_category(category_id, db)


@ads_router.delete("/{ad_id}", status_code=204)
async def delete_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    return await _delete_ad(ad_id, db)


@ads_router.patch("/ads/{ad_id}", response_model=Ads_sc)
async def update_ad(ad_id: int, update: AdUpdate_sc = Body(...), db: AsyncSession = Depends(get_db)):
    return await _update_ad(ad_id, db, update)

@ads_router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("indexB.html", {"request": request})


@ads_router.get("/newProduct", response_class=HTMLResponse)
async def new_product(request: Request):
    try:
        user_id = await get_current_user(request)
    except HTTPException:
        return RedirectResponse(url="http://localhost:8080/auth/login")

    return templates.TemplateResponse("newProduct.html", {"request": request})

@ads_router.get("/json", response_model=List[Ads_sc])
async def get_ads_json(db: AsyncSession = Depends(get_db)):
    return await _get_all_ads(db)

@ads_router.get("/search_json", response_model=List[Ads_sc])
async def get_search_json(db: AsyncSession = Depends(get_db),
                       q: str | None = Query(None, description="Search term for ads title or description")
):
    return await _get_search_ads(db,  search_term=q)

@ads_router.get("/dormitories/all", response_model=List[Dormitory_sc])
async def get_all_dormitories(db: AsyncSession = Depends(get_db)):
    from ads_service.db.models import Dormitory
    result = await db.execute(select(Dormitory))
    dorms = result.scalars().all()
    return [Dormitory_sc(id=dorm.id, name=dorm.name, adress=dorm.adress) for dorm in dorms]

@ads_router.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})

@ads_router.get("/foundAds", response_class=HTMLResponse)
async def serve_found_ads(request: Request):
    return templates.TemplateResponse("foundAds.html", {"request": request})

@ads_router.get("/categories/all", response_model=List[Category_sc])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    from ads_service.db.models import Categories
    result = await db.execute(select(Categories))
    categories = result.scalars().all()
    return [Category_sc(id=cat.id, name=cat.name) for cat in categories]

@ads_router.get("/get_product_by_category", response_model=List[Ads_sc])
async def get_product_by_category(db: AsyncSession = Depends(get_db),
                                  category_id: int = Query(...),):
    return await _get_ads_by_category(db, category_id)

# @ads_router.get("/api/products/by_category/{category_id}")
# async def get_products_by_category(db: AsyncSession = Depends(get_db), category_id: int):
#     products = _get_ads_by_category(db, category_id)  # Ваша функция для запроса к БД
#     return products

@ads_router.get("/foundByCategory/{category_id}", response_class=HTMLResponse)
async def serve_this_category_ads(request: Request, category_id: int):
    return templates.TemplateResponse(
        "thisCategory.html", {
        "request": request,
        "category_id": category_id
    })

@ads_router.get("/one_ad_json/{ad_id}", response_model=Ads_sc)
async def get_ad_json(ad_id:int, db: AsyncSession = Depends(get_db)):
    return await _get_one_ad(db, ad_id)


@ads_router.get("/profile")
async def redirect_to_profile(request: Request):
    return RedirectResponse(url="http://localhost:8080/user/profile")


@ads_router.get("/Product/{ad_id}", response_class=HTMLResponse)
async def product(request: Request, ad_id: int, db: AsyncSession = Depends(get_db)):
    try:
        ad = await _get_one_ad(db, ad_id)
        if not ad:
            raise HTTPException(status_code=404, detail="Объявление не найдено")

        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "ad_id": ad_id
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in product route: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ads_router.get("/user/profile/json/{user_id}")
async def proxy_user_profile(user_id: str, request: Request):
    """Proxy requests to user service to avoid CORS issues"""
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

            # Пробуем разные варианты URL для подключения к user service
            urls_to_try = [
                f"http://localhost:8080/user/profile/json/{user_id}",  # Если работает через localhost
                f"http://user-service:8080/user/profile/json/{user_id}",  # Docker compose имя
                f"http://127.0.0.1:8080/user/profile/json/{user_id}"  # Альтернативный localhost
            ]

            last_error = None
            for url in urls_to_try:
                try:
                    print(f"Trying to connect to: {url}")
                    response = await client.get(
                        url,
                        headers=headers,
                        cookies=cookies,
                        timeout=5.0  # Уменьшаем timeout для быстрой проверки
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

            # Если все URL не сработали, возвращаем ошибку
            print(f"All connection attempts failed. Last error: {last_error}")
            raise HTTPException(
                status_code=503,
                detail=f"Unable to connect to user service. Last error: {last_error}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in proxy_user_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

