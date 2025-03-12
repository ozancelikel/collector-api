from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str
    DB_DEBUG: bool = Field(default=False)
    SCRAPER_DOWNLOAD_ABS_PATH: str
    SCRAPER_FILE_DEST: str
    SCRAPER_DOWNLOAD_FILE_TYPE: str
    SCRAPER_FREQ: int
    SCRAPER_HOURLY: bool = Field(default=False)
    KONECTGDS_USERNAME: str
    KONECTGDS_PASSWORD: str
    KONECTGDS_URL: str
    DAVIS_INTERNAL_API_KEY: str
    DAVIS_EXTERNAL_API_URI: str
    DAVIS_EXTERNAL_API_SECRET: str
    DAVIS_EXTERNAL_API_KEY: str
    DAVIS_STATION_ID: str
    DAVIS_TRIGGER_FREQ: int

    class Config:
        env_file = ".env"

settings = Settings()
