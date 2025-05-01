import time
from datetime import timedelta

from alembic.util import status
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch
from uuid import UUID

from user_service import settings
from user_service.db.hashing import Hasher
from user_service.db.session import get_db
from user_service.db.dals import UserDAL
from user_service.api.models import Token
from typing import Optional
from user_service.db.security import create_access_token
from fastapi import HTTPException, status
from user_service.db.models import User
from jose import jwt, JWTError
from user_service.api.actions.auth import _get_user_by_email_auth, authenticate_user
login_router = APIRouter()

async def get_user_from_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login/token")),
                              db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        print("email is ", email)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await _get_user_by_email_auth(email=email, session=db)
    if user is None:
        raise credentials_exception
    return user


@login_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email, "some_data": [1, 2, 3]},
                                       expires_time=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@login_router.get("/test_token")
async def test_jwt_token(current_user: User = Depends(get_user_from_token)):
    return {"succees": True, "user": current_user}
