from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from user_service.db.hashing import Hasher
from user_service.db.dals import UserDAL
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from user_service.db.models import User
from user_service import settings
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.db.session import get_db


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


async def get_user_from_token(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> User:
    # Check for token in cookies first
    cookie_token = request.cookies.get("access_token")

    # If token exists in cookies, extract it
    if cookie_token and cookie_token.startswith("Bearer "):
        token = cookie_token.replace("Bearer ", "")
    else:
        # Fallback to Authorization header if needed
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Необходима авторизация",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = auth_header.replace("Bearer ", "")

    try:
        # Verify the token and extract user info
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        user_id = payload.get("user_id")

        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Неверный токен")

        async with db.begin():
            user_dal = UserDAL(db)
            user = await user_dal.get_user_by_email(email)

            if not user:
                raise HTTPException(status_code=401, detail="Пользователь не найден")

            return user

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )