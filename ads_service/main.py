import uvicorn
from fastapi import FastAPI
from ads_service import settings
from ads_service.api.handlers import ads_router
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

engine = create_async_engine(settings.ADS_DATABASE_URL, future=True, echo=True)

app = FastAPI(openapi_prefix="/ads")

# 2. Монтируем статику по пути /static. Nginx добавит префикс /ads
app.mount("/static", StaticFiles(directory="ads_service/static"), name="static")

app.include_router(ads_router, tags=["ads"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port = 8001)