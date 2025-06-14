from envparse import Env


env = Env()

ADS_DATABASE_URL = env.str(
    "ADS_DATABASE_URL",
    # default= "postgresql+asyncpg://postgres:postgres@localhost:5433/BazarTPU_ads"
    default= "postgresql+asyncpg://postgres:postgres@db1:5432/BazarTPU_ads"
)

ADS_SQLALC_URL = env.str(
    "ADS_SQLALC_URL",
    # default="postgresql://postgres:postgres@localhost:5432/BazarTPU_ads"
    default="postgresql://postgres:postgres@db1:5432/BazarTPU_ads"
)

# ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_MINUTES = env.str(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    default="30"
)

# ALGORITHM = "HS256"
ALGORITHM = env.str(
    "ALGORITHM",
    default="HS256"
)
# SECRET_KEY = "secret_key"
SECRET_KEY = env.str(
    "SECRET_KEY",
    default="secret_key"
)