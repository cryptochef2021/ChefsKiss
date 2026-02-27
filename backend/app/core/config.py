from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "StayAgg"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://stayagg:stayagg@localhost:5432/stayagg"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    DEEPL_API_KEY: str = ""
    GOOGLE_TRANSLATE_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
