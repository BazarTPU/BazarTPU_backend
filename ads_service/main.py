import uvicorn
from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ads_service import settings
from ads_service.api.handlers import ads_router
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

engine = create_async_engine(settings.ADS_DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


Base = declarative_base()

app = FastAPI()
main_api_router = APIRouter()

app.mount("/ads/static", StaticFiles(directory="ads_service/static"), name="static")

main_api_router.include_router(ads_router, prefix="/ads", tags=["ads"])
app.include_router(main_api_router)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://127.0.0.1:8001", "http://127.0.0.1:8002"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port = 8081)