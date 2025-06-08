from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from ads_service.db.models import Ads, Categories, Dormitory, AdPhoto
from typing import Optional, List
from uuid import UUID


class AdDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_ad(
        self,
        user_id: UUID,
        category_id: int,
        title: str,
        description: str,
        address: Optional[str],
        dormitory_id: Optional[int],
        price: float,
        photos: Optional[list] = None  # предполагаем, что фото будет добавляться отдельно
    ) -> Ads:
        new_ad = Ads(
            user_id=user_id,
            category_id=category_id,
            title=title,
            description=description,
            address=address,
            dormitory_id=dormitory_id,
            price=price,
        )

        # создаём объекты AdPhoto и добавляем их к объявлению
        if photos:
            new_ad.photos = [AdPhoto(file_path=photo_path) for photo_path in photos]

        self.db_session.add(new_ad)
        await self.db_session.flush()
        return new_ad


    async def get_ad_by_id(self, ad_id: int) -> Optional[Ads]:
        query = select(Ads).where(Ads.id == ad_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create_category(self, name: str) -> Categories:
        category = Categories(name=name)
        self.db_session.add(category)
        await self.db_session.flush()
        return category

    async def create_dormitory(self, name: str, adress: str) -> Dormitory:
        dorm = Dormitory(name=name, adress=adress)
        self.db_session.add(dorm)
        await self.db_session.flush()
        return dorm
