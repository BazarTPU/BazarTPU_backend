from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from user_service.db.hashing import Hasher
from user_service.db.dals import UserDAL


async def _get_user_by_email_auth(email: str, session: AsyncSession):
    async with session.begin():
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_email(email=email)


async def authenticate_user(email: str, password: str, db: AsyncSession):
    user = await _get_user_by_email_auth(email=email, session=db)
    if user is None:
        return
    if not Hasher.verify_password(password=password, hashed_password=user.hashed_password):
        return
    return user