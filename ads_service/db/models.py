from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID  # корректный UUID тип для PostgreSQL
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class Ads(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    address = Column(String, nullable=True)
    dormitory_id = Column(Integer, ForeignKey("dormitories.id"), nullable=True)
    price = Column(Float, nullable=False)

    # связи
    photos = relationship("AdPhoto", back_populates="ad", cascade="all, delete-orphan", lazy="joined")
    dormitory = relationship("Dormitory", back_populates="ads")
    category = relationship("Categories", back_populates="ads")


class Dormitory(Base):
    __tablename__ = "dormitories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    adress = Column(String, unique=True, nullable=True)

    # связь с объявлениями
    ads = relationship("Ads", back_populates="dormitory")


class AdPhoto(Base):
    __tablename__ = "ad_photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(Integer, ForeignKey("ads.id"), nullable=False)
    file_path = Column(String, nullable=False)

    ad = relationship("Ads", back_populates="photos")


class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=False)

    # связь с объявлениями
    ads = relationship("Ads", back_populates="category")
