import datetime

from typing_extensions import Optional
from datetime import timedelta
from user_service import settings
from jose import  jwt


def create_access_token(data:dict, expires_time: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_time:
        expire = datetime.datetime.utcnow() + expires_time
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt