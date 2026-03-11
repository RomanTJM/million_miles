import asyncio
import logging
import schedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import get_settings
from app.scrapers.carsensor import scrape_job

logger = logging.getLogger(__name__)
settings = get_settings()


async def start_scraper():
    if not settings.SCRAPER_ENABLED:
        logger.info("Скрапер отключен")
        return
    
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        scrape_job,
        "interval",
        seconds=settings.SCRAPER_INTERVAL_SECONDS,
        id="scraper_job",
        name="Periodic car scraping",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info(f"Скрапер запущен. Интервал: {settings.SCRAPER_INTERVAL_SECONDS} секунд")
    
    await scrape_job()
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Скрапер остановлен")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_scraper())
