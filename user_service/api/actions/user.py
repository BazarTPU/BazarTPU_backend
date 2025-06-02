from uuid import UUID

from select import select

from user_service.db.hashing import Hasher
from user_service.db.dals import UserDAL
from user_service.api.models import User_sc
from fastapi import HTTPException

from user_service.db.models import Dormitory


async def _create_new_user(body: User_sc, session) -> User_sc:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            hashed_password = Hasher.hash_password(password=body.password)
        )
        return User_sc(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.hashed_password,
        )


async def _delete_user_by_id(user_id: UUID, session) -> dict:
    async with session.begin():
        user_dal = UserDAL(session)
        success = await user_dal.delete_user_by_id(user_id)
        if success:
            return {"message": f"Пользователь {user_id} удалён"}
        return {"error": f"Пользователь {user_id} не найден"}



async def _get_user_by_id(user_id: UUID, session) -> User_sc:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return User_sc(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.hashed_password,
            phone_number=user.phone_number,
            telegram_id=user.telegram_id,
            dormitory=user.dormitory.name if user.dormitory else None,
            user_photo=user.photo[0].file_path if user.photo else "/static/img/noLogoItem900.png",
        )


async def _update_user_by_id(user_id: UUID, body: User_sc, session) -> User_sc:
    async with session.begin():
        user_dal = UserDAL(session)

        dormitory_id = None
        if body.dormitory:
            query = select(Dormitory).where(Dormitory.name == body.dormitory)
            result = await session.execute(query)
            dormitory = result.scalar_one_or_none()
            if dormitory:
                dormitory_id = dormitory.id

        updated_user = await user_dal.update_user_by_id(
            user_id=user_id,
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone_number=body.phone_number,
            telegram_id=body.telegram_id,
            dormitory_id=dormitory_id,
            user_photo=body.user_photo
        )
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден или поля не изменены")
        return User_sc(
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            email=updated_user.email,
            password=updated_user.hashed_password,
            phone_number=updated_user.phone_number,
            telegram_id=updated_user.telegram_id,
            dormitory=updated_user.dormitory.name if updated_user.dormitory else None,
            user_photo=updated_user.user_photo,
        )
