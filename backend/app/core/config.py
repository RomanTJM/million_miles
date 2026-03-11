from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Auto Listings API"
    DEBUG: bool = False
    
    SQLALCHEMY_DATABASE_URL: str = "postgresql://user:password@db:5432/auto_listings"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    SCRAPER_ENABLED: bool = True
    SCRAPER_INTERVAL_SECONDS: int = 3600  
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_RETRY_WAIT_SECONDS: int = 5
    
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ENABLED: bool = False
    
    OPENAI_API_KEY: str = ""

    SCRAPERAPI_KEY: str = ""
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
