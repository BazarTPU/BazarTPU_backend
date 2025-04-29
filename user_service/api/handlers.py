from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch
from uuid import UUID

from user_service.db.hashing import Hasher
from user_service.db.session import get_db
from user_service.db.dals import UserDAL
from user_service.api.models import User_sc
from typing import Optional
from user_service.api.actions.user import _get_user_by_id, _delete_user_by_id, _update_user_by_id, _create_new_user
from fastapi import HTTPException

user_router = APIRouter()


@user_router.post("/", response_model=User_sc)
async def create_user(body: User_sc, db: AsyncSession = Depends(get_db)):
    return await _create_new_user(body, db)

@user_router.delete("/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await _delete_user_by_id(user_id, db)

@user_router.get("/{user_id}", response_model=User_sc)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await _get_user_by_id(user_id, db)


@user_router.put("/{user_id}", response_model=User_sc)
async def update_user(user_id: UUID, body: User_sc, db: AsyncSession = Depends(get_db)):
    return await _update_user_by_id(user_id, body, db)
