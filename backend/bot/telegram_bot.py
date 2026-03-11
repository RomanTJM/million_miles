import logging
import asyncio
import os
from typing import Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
import asyncpg
from app.core.config import get_settings
from app.services.llm_service import get_llm_service, parse_query_simple

logger = logging.getLogger("bot")
settings = get_settings()


class BotStates(StatesGroup):
    waiting_for_query = State()


class TelegramBot:
    def __init__(self, db_pool: Optional[asyncpg.Pool] = None, llm_api_key: Optional[str] = None):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        self.pool = db_pool
        self.llm_service = get_llm_service(api_key=llm_api_key)
        self.register_handlers()

    def register_handlers(self):
        self.dp.message.register(self.handle_start, Command("start"))
        self.dp.message.register(self.handle_latest_cars, Command("latest"))
        self.dp.message.register(self.handle_help, Command("help"))
        self.dp.message.register(self.handle_search_query, F.text)

    async def handle_start(self, message: Message):
        welcome_text = (
            "Добро пожаловать в бот авто-объявлений!\n\n"
            "**Как это работает:**\n"
            "Просто напишите мне запрос в свободной форме:\n\n"
            "Примеры запросов:\n"
            "• Найди красную BMW до 2 млн\n"
            "• Дорогие машины 2023 года\n"
            "• Toyota Camry от 2015 года\n"
            "• Белый автомобиль до 3 млн\n\n"
            "Я использую AI для понимания вашего запроса!\n\n"
            "Доступные команды:\n"
            "/latest - показать последние 5 объявлений\n"
            "/help - справка"
        )
        await message.answer(welcome_text)

    async def handle_latest_cars(self, message: Message):
        if not self.pool:
            await message.answer(" Нет подключения к БД")
            return

        try:
            cars = await self.pool.fetch(
                """
                SELECT brand, model, year, price, color, url
                FROM cars
                WHERE is_active = true
                ORDER BY created_at DESC
                LIMIT 5
                """
            )

            if not cars:
                await message.answer(" Объявлений не найдено")
                return

            text = "**Последние 5 объявлений:**\n\n"
            for i, car in enumerate(cars, 1):
                price_str = f"{car['price']:,.0f}".replace(",", " ")
                text += (
                    f"{i}. **{car['brand']} {car['model']}** ({car['year']})\n"
                    f"   Цена: {price_str} ₽\n"
                    f"   Цвет: {car['color'] or 'не указан'}\n\n"
                )

            await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

        except Exception as e:
            logger.error(f"Ошибка получения объявлений: {e}")
            await message.answer("Ошибка при получении данных")

    async def handle_search_query(self, message: Message, state: FSMContext):
        query = message.text
        status_msg = await message.answer(" Анализирую ваш запрос... 🔍")

        try:
            if not self.pool:
                await message.answer("Нет подключения к БД")
                return

            logger.info(f"Парсим запрос: {query}")
            filters = {}
            if self.llm_service.is_available():
                filters = self.llm_service.parse_user_query(query)

            if not filters:
                filters = parse_query_simple(query)

            if not filters:
                await message.answer(
                    " Не смог понять ваш запрос.\n\n"
                    "Попробуйте:\n"
                    "• Найди BMW\n"
                    "• Машины до 2 млн\n"
                    "• Красный автомобиль\n"
                    "• Toyota 2020 года\n\n"
                    "/latest - показать последние объявления"
                )
                return

            search_conditions = ["is_active = true"]
            search_params = []

            def next_param():
                return f"${len(search_params) + 1}"

            if filters.get("brand"):
                search_conditions.append(f"LOWER(brand) LIKE LOWER({next_param()})")
                search_params.append(f"%{filters['brand']}%")

            if filters.get("model"):
                search_conditions.append(f"LOWER(model) LIKE LOWER({next_param()})")
                search_params.append(f"%{filters['model']}%")

            if filters.get("year_from"):
                search_conditions.append(f"year >= {next_param()}")
                search_params.append(filters["year_from"])

            if filters.get("year_to"):
                search_conditions.append(f"year <= {next_param()}")
                search_params.append(filters["year_to"])

            if filters.get("price_from"):
                search_conditions.append(f"price >= {next_param()}")
                search_params.append(filters["price_from"])

            if filters.get("price_to"):
                search_conditions.append(f"price <= {next_param()}")
                search_params.append(filters["price_to"])

            if filters.get("color"):
                search_conditions.append(f"LOWER(color) LIKE LOWER({next_param()})")
                search_params.append(f"%{filters['color']}%")

            where_clause = " AND ".join(search_conditions)
            sql_query = f"""
                SELECT brand, model, year, price, color, url
                FROM cars
                WHERE {where_clause}
                ORDER BY updated_at DESC
                LIMIT 10
            """

            logger.info(f"SQL: {sql_query} | params: {search_params}")
            cars = await self.pool.fetch(sql_query, *search_params)

            try:
                await status_msg.delete()
            except:
                pass

            if cars:
                text = f" **Найдено объявлений:** {len(cars)}\n\n"

                for i, car in enumerate(cars[:5], 1):
                    price_str = f"{car['price']:,.0f}".replace(",", " ")
                    text += (
                        f"{i}. **{car['brand']} {car['model']}** ({car['year']})\n"
                        f"    {price_str} ₽\n"
                        f"    {car['color'] or 'не указан'}\n"
                        f"\n"
                    )

                if len(cars) > 5:
                    text += f"... и ещё {len(cars) - 5} объявлений"

                await message.answer(text, parse_mode="Markdown")
                logger.info(f"Найдено {len(cars)} машин по запросу: {query}")
            else:
                await message.answer(
                    " По вашему запросу ничего не найдено\n\n"
                    "Попробуйте:\n"
                    "• Изменить цену\n"
                    "• Расширить диапазон лет\n"
                    "• /latest - показать все объявления"
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}")
            await message.answer(
                f" Ошибка при обработке запроса\n\n"
                f"Напишите проще: например 'BMW' или 'машины до 2 млн'"
            )

    async def handle_help(self, message: Message):
        help_text = (
            " **Справка**\n\n"
            " Я ищу автомобили через AI!\n\n"
            " Просто напишите:\n"
            "• Красная BMW до 3 млн\n"
            "• Toyota Camry 2020\n"
            "• Машины от 1 млн до 5 млн\n\n"
            " Команды:\n"
            "/start - начать\n"
            "/latest - последние объявления\n"
            "/help - эта справка\n\n"
            " Чем подробнее запрос - тем лучше результаты!"
        )
        await message.answer(help_text, parse_mode="Markdown")

    async def send_new_listings_notification(self, chat_id: int, cars: list):
        if not cars:
            return

        text = " **Новые объявления!** \n\n"
        for i, car in enumerate(cars[:5], 1):
            price_str = f"{car['price']:,.0f}".replace(",", " ")
            text += (
                f"{i}.  {car['brand']} {car['model']} ({car['year']})\n"
                f"    {price_str} ₽\n"
                f"    {car.get('color', 'не указан')}\n\n"
            )

        try:
            await self.bot.send_message(chat_id, text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")

    async def start(self):
        if not settings.TELEGRAM_ENABLED or not settings.TELEGRAM_BOT_TOKEN:
            logger.info("Telegram бот отключен")
            return

        try:
            if not self.pool:
                db_url = settings.SQLALCHEMY_DATABASE_URL
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
                self.pool = await asyncpg.create_pool(db_url)

            logger.info(" Telegram бот запущен")
            me = await self.bot.get_me()
            logger.info(f"Бот: @{me.username}")
            await self.dp.start_polling(self.bot)

        except Exception as e:
            logger.error(f" Ошибка запуска бота: {e}")
            raise
        finally:
            if self.pool:
                await self.pool.close()
            await self.bot.session.close()


async def run_bot():
    llm_api_key = os.getenv("OPENAI_API_KEY")
    bot = TelegramBot(llm_api_key=llm_api_key)
    await bot.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(run_bot())
