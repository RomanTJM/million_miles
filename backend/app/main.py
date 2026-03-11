import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db, dispose_db
from app.core.config import get_settings
from app.scrapers.carsensor import scrape_job
from app.routers import auth, cars

logger = logging.getLogger(__name__)
settings = get_settings()

_scraper_task = None
_bot_task = None


async def _scraper_loop():
    logger.info("Скрапер запущен как фоновая задача")
    while True:
        try:
            await scrape_job()
        except Exception as e:
            logger.error(f"Ошибка в цикле скрапера: {e}")
        logger.info(f"Следующий запуск скрапера через {settings.SCRAPER_INTERVAL_SECONDS} сек")
        await asyncio.sleep(settings.SCRAPER_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scraper_task, _bot_task
    await init_db()
    if settings.SCRAPER_ENABLED:
        _scraper_task = asyncio.create_task(_scraper_loop())
    if settings.TELEGRAM_ENABLED and settings.TELEGRAM_BOT_TOKEN:
        from bot.telegram_bot import run_bot
        _bot_task = asyncio.create_task(run_bot())
    yield
    if _scraper_task:
        _scraper_task.cancel()
    if _bot_task:
        _bot_task.cancel()
    await dispose_db()


app = FastAPI(
    title="Auto Listings API",
    description="API для управления объявлениями автомобилей",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cars.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
