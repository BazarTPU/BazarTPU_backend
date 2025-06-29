from envparse import Env


env = Env()

USER_DATABASE_URL = env.str(
    "USER_DATABASE_URL",
    default= "postgresql+asyncpg://postgres:postgres@db2:5432/BazarTPU_user"
    # default= "postgresql+asyncpg://postgres:postgres@localhost:5434/BazarTPU_user"
)


USER_SQLALC_URL = env.str(
    "SQLALC_URL",
    default="postgresql://postgres:postgres@db2:5432/BazarTPU_user"
    # default="postgresql://postgres:postgres@localhost:5434/BazarTPU_user"
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