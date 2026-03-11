import json
import logging
import os
import re
from typing import Optional, Dict, Any
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger("bot")


class CarFilters(BaseModel):
    brand: Optional[str] = Field(None, description="Марка автомобиля (например: BMW, Toyota)")
    model: Optional[str] = Field(None, description="Модель автомобиля (например: X5, Camry)")
    year_from: Optional[int] = Field(None, description="Минимальный год выпуска (например: 2015)")
    year_to: Optional[int] = Field(None, description="Максимальный год выпуска (например: 2023)")
    price_from: Optional[float] = Field(None, description="Минимальная цена в рублях (например: 1000000)")
    price_to: Optional[float] = Field(None, description="Максимальная цена в рублях (например: 3000000)")
    color: Optional[str] = Field(None, description="Цвет автомобиля (например: красный, синий, чёрный)")


class LLMService:
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "parse_car_filters",
                "description": "Извлечение параметров фильтрации автомобилей из текста на естественном языке",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brand": {
                            "type": "string",
                            "description": "Марка автомобиля (например: BMW, Toyota, Mercedes, Audi)"
                        },
                        "model": {
                            "type": "string",
                            "description": "Модель автомобиля (например: X5, Camry, E-Class)"
                        },
                        "year_from": {
                            "type": "integer",
                            "description": "Минимальный год выпуска (например: 2015)"
                        },
                        "year_to": {
                            "type": "integer",
                            "description": "Максимальный год выпуска (например: 2023)"
                        },
                        "price_from": {
                            "type": "number",
                            "description": "Минимальная цена в рублях (например: 1000000, 2.5e6)"
                        },
                        "price_to": {
                            "type": "number",
                            "description": "Максимальная цена в рублях (например: 3000000, 5e6)"
                        },
                        "color": {
                            "type": "string",
                            "description": "Цвет автомобиля (например: красный, синий, чёрный, белый)"
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        try:
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
                self._available = True
            else:
                self.client = None
                self._available = False
                logger.warning("OPENAI_API_KEY не установлен. LLM функции будут отключены.")
        except Exception as e:
            logger.error(f"Ошибка инициализации OpenAI клиента: {e}")
            self.client = None
            self._available = False

    def is_available(self) -> bool:
        return self._available and self.client is not None

    def parse_user_query(self, query: str) -> Dict[str, Any]:
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты помощник для поиска автомобилей. "
                        "Твоя задача - извлечь параметры фильтрации из запроса пользователя. "
                        "Используй функцию parse_car_filters для парсинга. "
                        "Если параметр не указан, оставь его пустым (null)."
                    )
                },
                {
                    "role": "user",
                    "content": query
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=self.TOOLS,
                tool_choice="auto",
                temperature=0.3,
            )

            if response.choices[0].finish_reason == "tool_calls":
                tool_calls = response.choices[0].message.tool_calls

                if tool_calls:
                    tool_call = tool_calls[0]
                    if tool_call.function.name == "parse_car_filters":
                        filters_data = json.loads(tool_call.function.arguments)
                        filters = CarFilters(**filters_data)
                        logger.info(f"Извлечены фильтры из запроса '{query}': {filters.model_dump(exclude_none=True)}")
                        return filters.model_dump(exclude_none=True)

            logger.warning(f"LLM не смог извлечь фильтры из: {query}")
            return {}

        except Exception as e:
            logger.error(f"Ошибка при парсинге запроса LLM: {e}")
            return {}

    def format_car_response(self, cars: list, query: str = "") -> str:
        if not cars:
            return (
                "По вашему запросу ничего не найдено.\n\n"
                "Попробуйте:\n"
                "• Изменить цену\n"
                "• Расширить запрос\n"
                "• Посмотреть все объявления (/latest)"
            )

        response = f"Найдено объявлений: {len(cars)}\n\n"

        for i, car in enumerate(cars[:5], 1):
            price_str = f"{car['price']:,.0f}".replace(",", " ")
            response += (
                f"#{i} 🚗 **{car['brand']} {car['model']}** ({car['year']})\n"
                f"💰 Цена: {price_str} ₽\n"
                f"🎨 Цвет: {car.get('color', 'не указан')}\n"
            )
            response += "\n"

        if len(cars) > 5:
            response += f"... и ещё {len(cars) - 5} объявлений"

        return response


def parse_query_simple(query: str) -> Dict[str, Any]:
    filters: Dict[str, Any] = {}
    text = query.lower().strip()

    brands = [
        "toyota", "тойота",
        "nissan", "ниссан",
        "honda", "хонда",
        "suzuki", "сузуки",
        "daihatsu", "дайхацу",
        "mazda", "мазда",
        "subaru", "субару",
        "mitsubishi", "митсубиши", "митсубиси",
        "bmw", "бмв",
        "mercedes", "мерседес",
        "audi", "ауди",
        "volkswagen", "фольксваген",
        "hyundai", "хёндай", "хундай",
        "kia", "киа",
        "lexus", "лексус",
        "ford", "форд",
        "chevrolet", "шевроле",
        "renault", "рено",
        "peugeot", "пежо",
        "volvo", "вольво",
    ]
    brand_map = {
        "тойота": "Toyota", "toyota": "Toyota",
        "ниссан": "Nissan", "nissan": "Nissan",
        "хонда": "Honda", "honda": "Honda",
        "сузуки": "Suzuki", "suzuki": "Suzuki",
        "дайхацу": "Daihatsu", "daihatsu": "Daihatsu",
        "мазда": "Mazda", "mazda": "Mazda",
        "субару": "Subaru", "subaru": "Subaru",
        "митсубиши": "Mitsubishi", "митсубиси": "Mitsubishi", "mitsubishi": "Mitsubishi",
        "бмв": "BMW", "bmw": "BMW",
        "мерседес": "Mercedes", "mercedes": "Mercedes",
        "ауди": "Audi", "audi": "Audi",
        "фольксваген": "Volkswagen", "volkswagen": "Volkswagen",
        "хёндай": "Hyundai", "хундай": "Hyundai", "hyundai": "Hyundai",
        "киа": "Kia", "kia": "Kia",
        "лексус": "Lexus", "lexus": "Lexus",
        "форд": "Ford", "ford": "Ford",
        "шевроле": "Chevrolet", "chevrolet": "Chevrolet",
        "рено": "Renault", "renault": "Renault",
        "пежо": "Peugeot", "peugeot": "Peugeot",
        "вольво": "Volvo", "volvo": "Volvo",
    }
    for b in brands:
        if re.search(r'\b' + re.escape(b) + r'\b', text):
            filters["brand"] = brand_map.get(b, b.capitalize())
            break

    m = re.search(r'до\s+(\d+(?:[.,]\d+)?)\s*млн', text)
    if m:
        filters["price_to"] = float(m.group(1).replace(",", ".")) * 1_000_000

    m = re.search(r'до\s+(\d+(?:[.,]\d+)?)\s*тыс', text)
    if m:
        filters["price_to"] = float(m.group(1).replace(",", ".")) * 1_000

    m = re.search(r'от\s+(\d+(?:[.,]\d+)?)\s*млн', text)
    if m:
        filters["price_from"] = float(m.group(1).replace(",", ".")) * 1_000_000

    m = re.search(r'от\s+(\d+(?:[.,]\d+)?)\s*тыс', text)
    if m:
        filters["price_from"] = float(m.group(1).replace(",", ".")) * 1_000

    m = re.search(r'от\s+(20\d{2})\s*г', text)
    if m:
        filters["year_from"] = int(m.group(1))

    m = re.search(r'до\s+(20\d{2})\s*г', text)
    if m:
        filters["year_to"] = int(m.group(1))

    m = re.search(r'\b(20\d{2})\s*год', text)
    if m and "year_from" not in filters:
        filters["year_from"] = int(m.group(1))
        filters["year_to"] = int(m.group(1))

    color_map = {
        "красн": "Красный", "белый": "Белый", "белая": "Белый",
        "чёрн": "Чёрный", "черн": "Чёрный",
        "серебр": "Серебристый", "серый": "Серый", "серая": "Серый",
        "синий": "Синий", "синяя": "Синий",
        "голуб": "Голубой",
        "зелён": "Зелёный", "зелен": "Зелёный",
        "желт": "Жёлтый",
        "коричн": "Коричневый",
        "оранж": "Оранжевый",
        "фиолет": "Фиолетовый",
        "розов": "Розовый",
    }
    for key, val in color_map.items():
        if key in text:
            filters["color"] = val
            break

    return filters


_llm_service: Optional[LLMService] = None


def get_llm_service(api_key: Optional[str] = None) -> LLMService:
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService(api_key=api_key)

    return _llm_service
