from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "car_parts_db"
    TFIDF_SIMILARITY_THRESHOLD: float = 0.05
    SEARCH_MIN_QUERY_LEN: int = 2
    MIN_REAL_PRICE: int = 50

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()