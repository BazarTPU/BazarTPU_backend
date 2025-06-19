from typing import Optional, List

import uuid
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from user_service.db.models import User, Dormitory


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self, first_name: str, last_name: str, email: str, hashed_password: str) -> User:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hashed_password,

        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user_by_id(self, user_id: uuid.UUID) -> bool:
        query = delete(User).where(User.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.rowcount > 0  # True if user was deleted

    async def update_user_by_id(
            self,
            user_id: uuid.UUID,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            email: Optional[str] = None,
            phone_number: Optional[str] = None,
            telegram_id: Optional[str] = None,
            dormitory_id: Optional[str] = None
    ) -> Optional[User]:
        # Убрали user_photo из параметров, так как работаем через отдельный endpoint
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if email is not None:
            update_data["email"] = email
        if phone_number is not None:
            update_data["phone_number"] = phone_number
        if telegram_id is not None:
            update_data["telegram_id"] = telegram_id
        if dormitory_id is not None:
            update_data["dormitory_id"] = dormitory_id

        if not update_data:
            return None

        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(**update_data)
            .returning(User)
        )
        result = await self.db_session.execute(query)
        updated_user = result.fetchone()
        return updated_user[0] if updated_user else None

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        query = (
            select(User)
            .options(
                joinedload(User.dormitory),
                joinedload(User.photo)
            )
            .where(User.user_id == user_id)
        )
        result = await self.db_session.execute(query)
        user = result.unique().scalar_one_or_none()
        return user


    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()
        return user


class DormitoryDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_dormitory(self, name: str, adress: str) -> Dormitory:
        new_dormitory = Dormitory(
            name=name,
            adress=adress
        )
        self.db_session.add(new_dormitory)
        await self.db_session.flush()
        return new_dormitory

    async def get_all_dormitories(self) -> List[Dormitory]:
        query = select(Dormitory).order_by(Dormitory.name)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_dormitory_by_id(self, dormitory_id: int) -> Optional[Dormitory]:
        query = select(Dormitory).where(Dormitory.id == dormitory_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_dormitory(
            self,
            dormitory_id: int,
            name: Optional[str] = None,
            adress: Optional[str] = None
    ) -> Optional[Dormitory]:
        query = select(Dormitory).where(Dormitory.id == dormitory_id)
        result = await self.db_session.execute(query)
        dormitory = result.scalar_one_or_none()

        if dormitory:
            if name is not None:
                dormitory.name = name
            if adress is not None:
                dormitory.adress = adress
            await self.db_session.flush()

        return dormitory

    async def delete_dormitory(self, dormitory_id: int) -> bool:
        query = select(Dormitory).where(Dormitory.id == dormitory_id)
        result = await self.db_session.execute(query)
        dormitory = result.scalar_one_or_none()

        if dormitory:
            await self.db_session.delete(dormitory)
            await self.db_session.flush()
            return True
        return False
