# Habit Tracker

Приложение для отслеживания привычек, состоящее из телеграм-бота (frontend) и FastAPI-сервиса (backend). Пользователи могут создавать, редактировать и удалять привычки, отмечать их выполнение и получать уведомления о необходимости выполнить привычки. Данные хранятся в PostgreSQL, а взаимодействие между сервисами осуществляется через API.

## Описание проекта

Проект состоит из двух основных компонентов:
- **Телеграм-бот**: Frontend-составляющая, через которую пользователи управляют своими привычками.
- **FastAPI-сервис**: Backend, отвечающий за обработку данных, их хранение и аутентификацию.

Дополнительно реализован сервисный скрипт для отправки уведомлений в заданное время.

## Используемые библиотеки

- **FastAPI** (`fastapi>=0.115.12,<0.116.0`) — фреймворк для API.
- **Uvicorn** (`uvicorn>=0.34.2,<0.35.0`) и **Gunicorn** (`gunicorn>=23.0.0,<24.0.0`) — серверы для FastAPI.
- **SQLAlchemy** (`sqlalchemy>=2.0.40,<3.0.0`) и **Asyncpg** (`asyncpg>=0.30.0,<0.31.0`) — для работы с PostgreSQL.
- **Alembic** (`alembic>=1.15.2,<2.0.0`) — миграции базы данных.
- **PyTelegramBotAPI** (`pytelegrambotapi>=4.26.0,<5.0.0`) — для телеграм-бота.
- **PyJWT** (`pyjwt>=2.10.1,<3.0.0`) — аутентификация через JWT.
- **APScheduler** (`apscheduler>=3.11.0,<4.0.0`) — планировщик задач для уведомлений.
- **Envparse** (`envparse>=0.2.0,<0.3.0`) — для чтения переменных окружения.
- **Supervisor** (`supervisor>=4.2.5,<5.0.0`) — управление процессами.
- **HTTPX** (`httpx>=0.28.1,<0.29.0`) и **AIOHTTP** (`aiohttp>=3.11.18,<4.0.0`) — асинхронные HTTP-запросы.
- **Passlib** (`passlib>=1.7.4,<2.0.0`) — хеширование паролей.
- **AIOFiles** (`aiofiles>=24.1.0,<25.0.0`) — асинхронная работа с файлами.
- **Redis** (`redis>=6.1.0,<7.0.0`) и **Aioredis** (`aioredis>=2.0.1,<3.0.0`) — кэширование.
- **Psycopg2-binary** (`psycopg2-binary>=2.9.10,<3.0.0`) — синхронный драйвер PostgreSQL.
- **Ruff** (`ruff>=0.11.11,<0.12.0`) — линтер для Python.
- **Poetry** — управление зависимостями.

## Установка и запуск

### Требования
- Docker и Docker Compose.

### Установка
1. Склонируй репозиторий:
   ```bash
   git clone https://github.com/your-repo/habit-tracker.git
   cd habit-tracker

2. Создай файл `.env`  и заполни переменные:
   - `BOT_TOKEN` — токен телеграм-бота, полученный от BotFather.
   - `DATABASE_URL` — строка подключения к PostgreSQL для асинхронного доступа, например, `postgresql+asyncpg://user:password@db:5432/habits`.
   - `SYNC_DATABASE_URL` — строка подключения для синхронного доступа, например, `postgresql+psycopg2://user:password@db:5432/habits`.
   - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — данные для подключения к PostgreSQL.
   - `REDIS_URL` — URL для подключения к Redis, например, `redis://redis:6379/1`.
   - `API_URL` — URL FastAPI-сервиса, например, `http://app:5000`.
   - `SECRET_KEY` — секретный ключ для JWT-токенов.

### Запуск
1. Собери и запусти контейнеры:
   ```bash
   docker compose up  build
   ```
2. Проверь доступность
- отправь команду /start боту в Telegram
### остановка
```bash
 docker compose down -v
```


## Лицензия

### MIT License
Проект *Microblog Backend* распространяется под лицензией MIT. 
Это означает, что вы можете свободно использовать, копировать, изменять, публиковать,
распространять и продавать этот проект при условии, 
что вы сохраняете уведомление об авторских правах и текст лицензии в любых копиях или производных работах.

**Полный текст лицензии:**
```markdown
MIT License

Copyright (c) 2025 Danila Goncharov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```