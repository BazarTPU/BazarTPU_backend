from sqlalchemy.orm import sessionmaker
from user_service import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
