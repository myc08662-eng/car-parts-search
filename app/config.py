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
    SEARCH_MAX_QUERY_LEN: int = 200
    MIN_REAL_PRICE: int = 50
    ALLOWED_DOMAINS: list[str] = [
        'ozon.ru', 'tachka.ru', 'trialli.ru', 'shop.polosedan.ru',
        'mobiland.auto', 'amag.ru', 'startvolt.com', 'baza.drom.ru',
        'v-avto.ru', 'autone.ru', 'koleso.ru', 'zapkorea.ru',
        'luzar.ru', 'carvilleshop.ru', 'ruli.ru', 'cars.marshall.parts'
    ]
    USER_AGENTS: list[str] = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    ]

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()