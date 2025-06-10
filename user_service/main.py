from typing import Optional

import uuid
import uvicorn
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException, Form, status
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.log import echo_property
from sqlalchemy.orm import sessionmaker
from sqlalchemy.testing import future
from fastapi.middleware.cors import CORSMiddleware
from user_service import settings
from user_service.api.auth_middleware import AuthMiddleware
from user_service.api.auth_router import auth_router
from user_service.api.user_router import user_router
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.staticfiles import StaticFiles

engine = create_async_engine(settings.USER_DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.add_middleware(AuthMiddleware)


app.mount("/static", StaticFiles(directory="user_service/static"), name="static")
# app.mount("/ads/static", StaticFiles(directory="ads_service/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://127.0.0.1:8002", "http://127.0.0.1:8001"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port = 8082)