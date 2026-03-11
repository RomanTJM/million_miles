import asyncio
import logging
import re
from datetime import datetime
from typing import List
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.core.config import get_settings
from app.scrapers.translations import (
    translate_brand,
    translate_color,
    translate_model,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class CarSensorScraper:

    def __init__(self):
        self.base_url = "https://www.carsensor.net"
        self.timeout = settings.SCRAPER_TIMEOUT
        self.max_retries = settings.SCRAPER_MAX_RETRIES

    def _build_url(self, page: int) -> str:
        if page == 1:
            target = f"{self.base_url}/usedcar/index.html"
        else:
            target = f"{self.base_url}/usedcar/index{page}.html"

        if settings.SCRAPERAPI_KEY:
            return f"http://api.scraperapi.com?api_key={settings.SCRAPERAPI_KEY}&url={target}&country_code=jp"
        return target

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(aiohttp.ClientError),
    )
    async def fetch_page(self, session: aiohttp.ClientSession, page: int) -> List[dict]:
        url = self._build_url(page)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
        }

        try:
            async with session.get(url, headers=headers, timeout=self.timeout) as response:
                if response.status != 200:
                    logger.error(f"Ошибка {response.status} при запросе к странице {page}")
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')

                items = soup.select('.js-mainCassette') or soup.select('.cassetteWrap')

                cars = []
                for item in items:
                    try:
                        title_link = item.select_one('.cassetteMain__link')
                        if not title_link or not title_link.get('href'):
                            continue

                        car_url = title_link['href']
                        if not car_url.startswith('http'):
                            car_url = f"{self.base_url}{car_url}"

                        id_match = re.search(r'detail/(.*?)/', car_url)
                        external_id = id_match.group(1) if id_match else f"cs_{abs(hash(car_url))}"

                        full_name_jp = title_link.get_text(strip=True)

                        title_h3 = item.select_one('.cassetteMain__title')
                        brand_p = title_h3.find_previous('p') if title_h3 else None
                        brand_jp = brand_p.get_text(strip=True) if brand_p else ""

                        if brand_jp:
                            brand = translate_brand(brand_jp)
                        else:
                            parts = re.split(r'[\s　]+', full_name_jp.strip())
                            brand = translate_brand(parts[0]) if parts else "Unknown"

                        model = translate_model(full_name_jp)

                        price_tag = (
                            item.select_one('.totalPrice__content')
                            or item.select_one('.totalPrice')
                            or item.select_one('.basePrice__mainPriceNum')
                            or item.select_one('.basePrice')
                        )
                        price = 0.0
                        if price_tag:
                            price_text = price_tag.get_text(strip=True)
                            price_match = re.search(r'([\d.]+)', price_text.replace(',', ''))
                            if price_match:
                                price_val = float(price_match.group(1))
                                if "万円" in price_text or price_val < 10000:
                                    price = price_val * 10000
                                else:
                                    price = price_val

                        year = 0
                        spec_list = item.select_one('.specList')
                        if spec_list:
                            for dt in spec_list.find_all('dt'):
                                if "年式" in dt.get_text():
                                    dd = dt.find_next('dd')
                                    if dd:
                                        year_match = re.search(r'(\d{4})', dd.get_text())
                                        if year_match:
                                            year = int(year_match.group(1))
                                    break

                        if not year:
                            year_str = item.find(string=re.compile(r'\b(19|20)\d{2}\b'))
                            if year_str:
                                m = re.search(r'(\d{4})', str(year_str))
                                if m:
                                    year = int(m.group(1))

                        color = None
                        body_info = item.select('.carBodyInfoList__item')
                        if len(body_info) >= 2:
                            raw_color = body_info[1].get_text(strip=True)
                            if raw_color:
                                color = translate_color(raw_color)

                        if not color:
                            color_tip = item.select_one('.cassetteColorTip')
                            if color_tip:
                                raw_color = color_tip.parent.get_text(strip=True)
                                if raw_color:
                                    color = translate_color(raw_color)

                        cars.append({
                            "brand": brand,
                            "model": model,
                            "year": year,
                            "price": price,
                            "color": color,
                            "url": car_url,
                            "external_id": external_id,
                        })
                    except Exception as e:
                        logger.debug(f"Пропуск объявления из-за ошибки парсинга: {e}")
                        continue

                return cars
        except asyncio.TimeoutError:
            logger.error(f"Тайм-аут при запросе страницы {page}")
            return []
        except Exception as e:
            logger.error(f"Непредвиденная ошибка на странице {page}: {e}")
            return []

    async def fetch_listings(self, session: aiohttp.ClientSession) -> List[dict]:
        all_cars = []
        for page in range(1, 4):
            cars = await self.fetch_page(session, page)
            if not cars:
                break
            all_cars.extend(cars)
            await asyncio.sleep(1)

        logger.info(f"Всего собрано {len(all_cars)} реальных объявлений с {page} страниц")
        return all_cars

    async def upsert_cars(self, cars: List[dict], pool: asyncpg.Pool) -> tuple:
        created = 0
        updated = 0

        for car in cars:
            try:
                existing = await pool.fetchrow(
                    "SELECT id FROM cars WHERE external_id = $1",
                    car.get("external_id")
                )

                if existing:
                    await pool.execute(
                        """
                        UPDATE cars
                        SET brand = $1, model = $2, year = $3, price = $4,
                            color = $5, updated_at = NOW()
                        WHERE external_id = $6
                        """,
                        car["brand"],
                        car["model"],
                        car["year"],
                        car["price"],
                        car["color"],
                        car["external_id"]
                    )
                    updated += 1
                    logger.debug(f"Обновлена машина: {car['brand']} {car['model']}")
                else:
                    await pool.execute(
                        """
                        INSERT INTO cars
                        (brand, model, year, price, color, url,
                         external_id, source, is_active, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
                        """,
                        car["brand"],
                        car["model"],
                        car["year"],
                        car["price"],
                        car["color"],
                        car["url"],
                        car["external_id"],
                        "carsensor",
                        True
                    )
                    created += 1
                    logger.debug(f"Создана новая машина: {car['brand']} {car['model']}")

            except asyncpg.UniqueViolationError:
                logger.warning(f"Дубликат для {car.get('external_id')}, пропускаем")
                continue
            except Exception as e:
                logger.error(f"Ошибка при сохранении машины {car.get('external_id')}: {e}")
                continue

        return created, updated

    async def log_scraping(
        self,
        pool: asyncpg.Pool,
        status: str,
        message: str,
        items_scraped: int,
        items_created: int,
        items_updated: int,
        execution_time: float
    ):
        try:
            await pool.execute(
                """
                INSERT INTO scraper_logs
                (status, message, items_scraped, items_created, items_updated,
                 execution_time_seconds, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                status,
                message,
                items_scraped,
                items_created,
                items_updated,
                execution_time
            )
        except asyncpg.exceptions.UndefinedTableError:
            logger.warning("Таблица scraper_logs не существует. Пытаюсь создать...")
            try:
                await pool.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scraper_logs (
                        id SERIAL PRIMARY KEY,
                        status VARCHAR(50),
                        message TEXT,
                        items_scraped INTEGER,
                        items_created INTEGER,
                        items_updated INTEGER,
                        execution_time_seconds FLOAT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                    """
                )
                await pool.execute(
                    """
                    INSERT INTO scraper_logs
                    (status, message, items_scraped, items_created, items_updated,
                     execution_time_seconds, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, NOW())
                    """,
                    status,
                    message,
                    items_scraped,
                    items_created,
                    items_updated,
                    execution_time
                )
                logger.info("Таблица scraper_logs успешно создана и запись добавлена")
            except Exception as e:
                logger.error(f"Ошибка при создании/записи в scraper_logs: {e}")
        except Exception as e:
            logger.error(f"Ошибка логирования скрапинга: {e}")


async def scrape_job():
    logger.info("Начало скрапинга...")
    start_time = datetime.now()

    scraper = CarSensorScraper()

    try:
        db_url = settings.SQLALCHEMY_DATABASE_URL
        if not db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

        pool = await asyncpg.create_pool(db_url)
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        return

    try:
        async with aiohttp.ClientSession() as session:
            cars = await scraper.fetch_listings(session)
            created, updated = await scraper.upsert_cars(cars, pool)

            execution_time = (datetime.now() - start_time).total_seconds()
            status = "success" if created + updated > 0 else "partial"
            message = f"Собрано {len(cars)}, создано {created}, обновлено {updated}"

            await scraper.log_scraping(
                pool, status, message, len(cars), created, updated, execution_time
            )

            logger.info(f"Скрапинг завершен: {message}. Время: {execution_time}с")

    except Exception as e:
        logger.error(f"Ошибка скрапинга: {e}")
        execution_time = (datetime.now() - start_time).total_seconds()
        await scraper.log_scraping(pool, "error", str(e), 0, 0, 0, execution_time)
    finally:
        await pool.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(scrape_job())
