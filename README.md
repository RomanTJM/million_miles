# MillionMiles — Сервис автомобильных объявлений

Веб-приложение для просмотра объявлений о продаже автомобилей. Данные собираются со стороннего сайта автоматически, хранятся в PostgreSQL и отображаются через React-интерфейс. Telegram-бот для поиска через чат https://t.me/BOT_million_miles_bot.

## Технологии

**Backend:** FastAPI, SQLAlchemy (async), PostgreSQL, Alembic, JWT, aiohttp, tenacity
**Frontend:** React 18, Vite, Zustand, Axios
**Bot:** aiogram 3, OpenAI Function Calling
**DevOps:** Docker, Docker Compose

## Запуск через Docker (рекомендуется)

```bash
git clone https://github.com/RomanTJM/million_miles.git
cd million_miles

docker-compose up --build
```

После запуска:
- Фронтенд: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger документация: http://localhost:8000/docs

Логин по умолчанию: `admin` / `admin123`

## Остановка Docker

```bash
docker-compose down          
```

## Локальный запуск (без Docker)

#### Backend

```bash
cd backend

python -m venv venv
source venv/bin/activate  

pip install -r requirements.txt

cp .env.example .env

python app/seeds.py          
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Структура проекта

```
million_miles/
├── backend/
│   ├── app/
│   │   ├── core/          # config, database, security (JWT)
│   │   ├── models/        # SQLAlchemy модели (User, Car, ScraperLog)
│   │   ├── schemas/       # Pydantic схемы запросов/ответов
│   │   ├── routers/       # API маршруты (auth, cars)
│   │   ├── scrapers/      # парсер carsensor.net + воркер
│   │   ├── services/      # LLM-сервис для бота
│   │   ├── seeds.py       # инициализация БД (admin-пользователь)
│   │   └── main.py        # точка входа FastAPI
│   ├── bot/
│   │   └── telegram_bot.py
│   ├── alembic/           # миграции БД
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/         # Login.jsx, Home.jsx
│   │   ├── components/    # Header.jsx,ProtectedRoute.jsx, SearchBar.jsx, Sidebar.jsx
│   │   ├── stores/        # authStore.js, carsStore.js (Zustand)
│   │   ├── utils/         # api.js (Axios + interceptors)
│   │   └── styles/
│   └── vite.config.js
├── docker-compose.yml
└── docker-compose.prod.yml
```

## API

### Аутентификация

POST `/api/login` # Вход, возвращает JWT токен 
POST `/api/register` # Регистрация нового пользователя

### Объявления (требует Authorization: Bearer {token})

GET `/api/cars` # Список с фильтрацией и пагинацией 
GET `/api/cars/{id}` # Одно объявление 
POST `/api/cars` # Создать объявление 
PUT `/api/cars/{id}` # Обновить объявление 
DELETE `/api/cars/{id}` # Деактивировать объявление 
GET `/health` # Проверка состояния API 

**Параметры GET /api/cars:**
`page`, `page_size`, `brand`, `model`, `year_from`, `year_to`, `price_from`, `price_to`

## Конфигурация

Скопируйте `backend/.env.example` в `backend/.env` и заполните:

```env
SQLALCHEMY_DATABASE_URL=postgresql://user:password@db:5432/auto_listings
SECRET_KEY=замените-на-случайную-строку
SCRAPER_ENABLED=true
SCRAPER_INTERVAL_SECONDS=3600

# Telegram бот (опционально)
TELEGRAM_BOT_TOKEN=токен-от-BotFather
TELEGRAM_ENABLED=false
OPENAI_API_KEY=ключ-openai-для-умного-поиска
```

## Telegram-бот

https://t.me/BOT_million_miles_bot

Бот поддерживает поиск на русском языке:

```
Найди красную BMW до 2 млн
Toyota Camry 2020 года
Машины от 1 до 3 млн
```

При наличии `OPENAI_API_KEY` запросы парсит GPT, иначе — встроенный regex-парсер.

Команды: `/start`, `/latest`, `/help`

## Тесты

```bash
cd backend
pytest -v
```