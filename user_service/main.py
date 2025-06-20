import uvicorn
from fastapi import FastAPI
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from user_service import settings
from user_service.api.auth_middleware import AuthMiddleware
from user_service.api.auth_router import auth_router
from user_service.api.user_router import user_router
from fastapi.staticfiles import StaticFiles
app = FastAPI(openapi_prefix="/auth")

app.include_router(auth_router)
app.include_router(user_router, prefix="/user")

app.add_middleware(AuthMiddleware)

# 3. Монтируем статику по пути /static. Nginx будет обрабатывать это.
app.mount("/static", StaticFiles(directory="user_service/static"), name="static")
app.mount("/media", StaticFiles(directory="user_service/media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port = 8002)