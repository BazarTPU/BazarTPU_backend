from envparse import Env


env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default= "postgresql+asyncpg://postgres:postgres@localhost:5433/BazarTPU_ads"
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

ALGORITHM = "HS256"
SECRET_KEY = "secret_key"