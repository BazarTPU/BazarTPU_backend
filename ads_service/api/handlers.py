from fastapi import APIRouter, Depends, Body, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch
from typing import List

from ads_service.db.session import get_db
from ads_service.api.models import Ads_sc, Category_sc, Dormitory_sc, AdUpdate_sc
from ads_service.api.actions.ads import _create_new_ad, _create_new_category, _create_new_dormitory, _delete_dormitory, \
    _delete_ad, _delete_category, _update_ad, _get_all_ads
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
templates = Jinja2Templates(directory="ads_service/templates")


ads_router = APIRouter()


@ads_router.post("/create_new_ad", response_model=Ads_sc)
async def create_new_ad(
    user_id: str = Form(...),
    category_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(None),
    dormitory_id: int = Form(None),
    price: float = Form(...),
    photos: list[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
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
    return await _create_new_dormitory(body, db)


@ads_router.delete("/dormitories/{dormitory_id}", status_code=204)
async def delete_dormitory(dormitory_id: int, db: AsyncSession = Depends(get_db)):
    return await _delete_dormitory(dormitory_id, db)


@ads_router.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    return await _delete_category(category_id, db)


@ads_router.delete("/ads/{ad_id}", status_code=204)
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
    return templates.TemplateResponse("newProduct.html", {"request": request})

@ads_router.get("/json", response_model=List[Ads_sc])
async def get_ads_json(db: AsyncSession = Depends(get_db)):
    return await _get_all_ads(db)