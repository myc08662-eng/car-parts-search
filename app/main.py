from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
import os

from app.config import get_settings
from app.templating import templates
from app.routers import search, instructions, categories
from app.services import search_service
from app.repositories import part_repo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Загрузка поискового индекса")
    try:
        parts = part_repo.get_all_parts_with_links()
        if parts:
            search_service.search_engine.fit(parts)
            app.state.search_ready = True
            logger.info(f"TF-IDF модель обучена на {len(parts)} запчастях")
        else:
            app.state.search_ready = False
            logger.warning("Нет данных для обучения поиска")
    except Exception as e:
        logger.error(f"Ошибка при загрузке поискового индекса: {e}")
        app.state.search_ready = False
    
    yield
    
    # Shutdown
    logger.info("Выключение сервера")

app = FastAPI(title="Car Parts Search v2", lifespan=lifespan)

# Статика
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Роутеры
app.include_router(search.router)
app.include_router(instructions.router)
app.include_router(categories.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)