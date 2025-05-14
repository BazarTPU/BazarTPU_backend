from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, DateTime, UUID, ForeignKey
from sqlalchemy.sql import func

import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String)
    telegram_id = Column(String)
    dormitory_id = Column(Integer, ForeignKey('dormitories.id'))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    hashed_password = Column(String, nullable=False)

    dormitory = relationship("Dormitory", back_populates="users", lazy="joined")
    photo = relationship("UserPhoto", back_populates="user", cascade="all, delete-orphan")


class UserPhoto(Base):
    __tablename__ = 'user_photo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    file_path = Column(String, nullable=False)

    user = relationship("User", back_populates="photo")


class Dormitory(Base):
    __tablename__ = 'dormitories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    adress = Column(String, unique=True)

    users = relationship("User", back_populates="dormitory")

