from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool

    class Config:
        env_file = ".env"

settings = Settings()
