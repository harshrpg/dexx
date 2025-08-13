from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Fetch below from secrets
    CRYPTOPANIC_API_KEY: str
    MOBULA_PRODUCTION_API_ENDPOINT: str
    DEEPSEEK_API_KEY: str
    ASI1_API_KEY: str
    MORALIS_API_KEY: str
    OPENAI_API_KEY: str
    REDIS_UNAME: str
    REDIS_PORT: int
    REDIS_PWD: str
    REDIS_HOST: str
    SECRET_KEY: str = "your-secret-key-here"
    # REDIS_HOST: str = "localhost"
    # REDIS_PORT: int = 6379
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_CONTEXT_MESSAGES: int = 10
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/token_insights"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
