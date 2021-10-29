from pydantic import BaseSettings


class Settings(BaseSettings):
    API_URL: str = '127.0.0.1:8000'


settings = Settings()

