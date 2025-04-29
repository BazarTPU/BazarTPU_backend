from typing import Optional

import uuid
from sqlalchemy import delete, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from user_service.db.models import User


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
            user_photo: Optional[str] = None
    ) -> Optional[User]:
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
        if user_photo is not None:
            update_data["user_photo"] = user_photo

        if not update_data:
            return None  # Нечего обновлять

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
        query = select(User).where(User.user_id == user_id)
        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()
        return user


    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()
        return user
