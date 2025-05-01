from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, UUID
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
    dormitory = Column(String)
    user_photo = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    hashed_password = Column(String, nullable=False)
