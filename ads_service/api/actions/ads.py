from re import search

from sqlalchemy import select, delete, or_
from sqlalchemy.orm import selectinload

from ads_service.db.dals import AdDAL
from ads_service.api.models import Ads_sc, Category_sc, Dormitory_sc, AdUpdate_sc
from fastapi import HTTPException, Body

from ads_service.db.models import Categories, Dormitory, Ads, AdPhoto


async def _create_new_ad(body: Ads_sc, session) -> Ads_sc:
    async with session.begin():
        ad_dal = AdDAL(session)
        ad = await ad_dal.create_ad(
            user_id=body.user_id,
            category_id=body.category_id,
            title=body.title,
            description=body.description,
            address=body.address,
            dormitory_id=body.dormitory_id,
            price=body.price,
            photos=body.photos,
        )
        # Подгружаем объявление с фотографиями через selectinload
        result = await session.execute(
            select(Ads).options(selectinload(Ads.photos)).where(Ads.id == ad.id)
        )
        ad_with_photos = result.scalar_one()
        return Ads_sc(
            user_id=ad_with_photos.user_id,
            category_id=ad_with_photos.category_id,
            title=ad_with_photos.title,
            description=ad_with_photos.description,
            address=ad_with_photos.address,
            dormitory_id=ad_with_photos.dormitory_id,
            price=ad_with_photos.price,
            photos=[photo.file_path for photo in ad_with_photos.photos] if ad_with_photos.photos else None
        )


async def _get_ad_by_id(ad_id: int, session) -> Ads_sc:
    async with session.begin():
        ad_dal = AdDAL(session)
        ad = await ad_dal.get_ad_by_id(ad_id)
        if not ad:
            raise HTTPException(status_code=404, detail="Объявление не найдено")
        return Ads_sc(
            id=ad.id,
            user_id=ad.user_id,
            category_id=ad.category_id,
            title=ad.title,
            description=ad.description,
            address=ad.address,
            dormitory_id=ad.dormitory_id,
            price=ad.price,
            photos=ad.photos,
        )

async def _create_new_category(body: Category_sc, session)-> Category_sc:
    async with session.begin():
        ad_dal = AdDAL(session)
        existing = await session.execute(select(Categories).where(Categories.name == body.name))
        if existing.scalar():
            raise HTTPException(status_code=400, detail="Категория уже существует")
        category = await ad_dal.create_category(name=body.name)
        return Category_sc(name=category.name)



async def _create_new_dormitory(body: Dormitory_sc, session)-> Dormitory_sc:
    async with session.begin():
        ad_dal = AdDAL(session)
        existing = await session.execute(select(Dormitory).where(Dormitory.name == body.name))
        if existing.scalar():
            raise HTTPException(status_code=400, detail="Общежитие уже существует")
        dormitory = await ad_dal.create_dormitory(name=body.name, adress=body.adress)
        return Dormitory_sc(name=dormitory.name, adress=dormitory.adress)

async def _delete_dormitory(dormitory_id: int, session):
    async with session.begin():
        result = await session.execute(delete(Dormitory).where(Dormitory.id == dormitory_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Общежитие не найдено")

async def _delete_category(category_id: int, session):
    async with session.begin():
        result = await session.execute(delete(Categories).where(Categories.id == category_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Категория не найдена")


async def _delete_ad(ad_id: int, session):
    async with session.begin():
        # Получаем объект объявления
        result = await session.execute(select(Ads).where(Ads.id == ad_id))
        ad = result.unique().scalar_one_or_none()

        if ad is None:
            raise HTTPException(status_code=404, detail="Объявление не найдено")

        # Удаляем через ORM
        await session.delete(ad)
        await session.flush()

async def _update_ad(ad_id: int, session,  update: AdUpdate_sc = Body(...)):
    async with session.begin():
        ad_dal = AdDAL(session)
        ad = await ad_dal.get_ad_by_id(ad_id)
        if not ad:
            raise HTTPException(status_code=404, detail="Объявление не найдено")

        # обновление полей
        for field, value in update.dict(exclude_unset=True).items():
            if field == "photos":
                ad.photos = [AdPhoto(file_path=path) for path in value]
            else:
                setattr(ad, field, value)

        await session.flush()

        return Ads_sc(
            id=ad.id,
            user_id=ad.user_id,
            category_id=ad.category_id,
            title=ad.title,
            description=ad.description,
            address=ad.address,
            dormitory_id=ad.dormitory_id,
            price=ad.price,
            photos=[photo.file_path for photo in ad.photos] if ad.photos else None,
        )

# отдаёт все объявления
async def _get_all_ads(session):
    async with session.begin():
        ad_dal = AdDAL(session)
        result = await session.execute(select(Ads))
        ads = result.unique().scalars().all()
        return [
            Ads_sc(
                id=ad.id,
                user_id=ad.user_id,
                category_id=ad.category_id,
                title=ad.title,
                description=ad.description,
                address=ad.address,
                dormitory_id=ad.dormitory_id,
                price=ad.price,
                photos=[photo.file_path for photo in ad.photos] if ad.photos else None
            ) for ad in ads
        ]

# отдаёт результаты поиска
async def _get_search_ads(session, search_term: str | None = None):
    async with session.begin():
        stmt = select(Ads).options(selectinload(Ads.photos))

        if search_term:
            search_pattern = f"%{search_term}%"

            stmt = stmt.where(
                or_(
                    Ads.title.ilike(search_pattern),
                    Ads.description.ilike(search_pattern),
                    Ads.address.ilike(search_pattern)
                )
            )

        stmt = stmt.order_by(Ads.id.desc())
        result = await session.execute(stmt)
        ads = result.unique().scalars().all()
        return [
            Ads_sc(
                id=ad.id,
                user_id=ad.user_id,
                category_id=ad.category_id,
                title=ad.title,
                description=ad.description,
                address=ad.address,
                dormitory_id=ad.dormitory_id,
                price=ad.price,
                photos=[photo.file_path for photo in ad.photos] if ad.photos else None
            ) for ad in ads
        ]

async def _get_ads_by_category(session, category_id: int):
    async with session.begin():
        stmt = select(Ads).options(selectinload(Ads.photos)).where(Ads.category_id==category_id)

        stmt = stmt.order_by(Ads.id.desc())
        result = await session.execute(stmt)
        ads = result.unique().scalars().all()
        return [
            Ads_sc(
                id=ad.id,
                user_id=ad.user_id,
                category_id=ad.category_id,
                title=ad.title,
                description=ad.description,
                address=ad.address,
                dormitory_id=ad.dormitory_id,
                price=ad.price,
                photos=[photo.file_path for photo in ad.photos] if ad.photos else None
            ) for ad in ads
        ]