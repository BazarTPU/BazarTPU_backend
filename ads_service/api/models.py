from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class Ads_sc(BaseModel):
    id: Optional[int] = None
    user_id: UUID
    category_id: int
    title: str
    description: str
    address: Optional[str] = None
    dormitory_id: Optional[int] = None
    price: float
    photos: Optional[List[str]] = None  # список путей к фото


class AdUpdate_sc(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    dormitory_id: Optional[int] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    photos: Optional[List[str]] = None


class Category_sc(BaseModel):
    name: str


class Dormitory_sc(BaseModel):
    name: str
