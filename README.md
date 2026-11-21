# FastDelivery — Fullstack E-commerce & Delivery Platform



Асинхронный высоконагруженный REST API сервис для платформы доставки и электронной коммерции с демонстрационным SPA-фронтендом на **Vue 3**, обратным проксированием через **Nginx**, кэшированием и хранением сессий в **Redis**, автоматическим CI-тестированием и подтвержденной оптимизацией производительности под нагрузкой.

---

## ✨ Основной функционал

* **Аутентификация и безопасность:**
  * Регистрация и авторизация пользователей с использованием **JWT (JSON Web Tokens)**.
  * Неблокирующее асинхронное хэширование паролей (`bcrypt` вынесен в `run_in_threadpool` без блокировки Event Loop).
  * Система инвалидации токенов при выходе из аккаунта (**Token Blacklist**).
  * Ролевая модель доступа (`buyer`, `seller`).
* **Каталог и товары:**
  * Управление карточками товаров и категориями (создание и редактирование доступно для роли `seller`).
  * Валидация входящих и исходящих данных через **Pydantic v2**.
* **Корзина покупок (Redis):**
  * Высокоскоростное хранение корзины в **Redis** с привязкой к пользователю.
  * Добавление, обновление количества и удаление позиций, динамический расчет итоговой стоимости.
* **Управление заказами:**
  * Атомарное оформление заказа из корзины в рамках единой транзакции БД с автоматической очисткой корзины в Redis.
  * Просмотр истории заказов пользователя с жадной подгрузкой позиций (`selectinload`).
  * Управление статусами заказа (`Unpaid`, `Paid`, `Processing`, `Shipped`, `Delivered`, `Cancelled`).
* **Веб-интерфейс и API Inspector (Vue 3 + Nginx):**
  * Легкий SPA-фронтенд на Vue 3 (Composition API) с панелью покупателя, кабинетом продавца и встроенным **API Inspector** для просмотра сырых JSON-ответов и HTTP-статусов в реальном времени.

---

## 🛠 Технологический стек

* **Backend:** Python 3.11+, FastAPI, Uvicorn (Multi-worker)
* **База данных и кэш:** PostgreSQL 15, SQLAlchemy 2.0 (Async), `asyncpg`, Alembic, Redis 7
* **Frontend & Proxy:** Vue 3 (Composition API), Tailwind CSS, Nginx (Reverse Proxy)
* **Безопасность и валидация:** Pydantic v2, PyJWT, Bcrypt
* **Тестирование и QA:** Pytest, Pytest-Asyncio, Locust (Load & Stress testing)
* **DevOps & CI/CD:** Docker, Docker Compose, GitHub Actions

---

## 📂 Структура проекта

```text
fast-delivery/
├── .github/
│   └── workflows/            # CI/CD пайплайн GitHub Actions (автозапуск Pytest)
├── backend/
│   ├── alembic/              # Миграции базы данных
│   ├── app/
│   │   ├── core/             # Конфигурация, пул подключений БД, async-безопасность, исключения
│   │   ├── models/           # ORM-модели SQLAlchemy (User, Product, Order, TokenBlackList)
│   │   ├── repositories/     # Слой доступа к данным (Repository Pattern)
│   │   ├── routes/           # Эндпоинты API (версионирование /api/v1)
│   │   ├── schemas/          # Pydantic-схемы валидации запросов и ответов
│   │   └── services/         # Бизнес-логика приложения (Service Layer)
│   ├── tests/                # Интеграционные и unit-тесты (Pytest)
│   ├── Dockerfile            # Образ FastAPI-приложения
│   └── requirements.txt      # Зависимости Python
├── frontend/
│   ├── index.html            # SPA-интерфейс на Vue 3 + панель API Inspector
│   └── app.js                # Логика работы с JWT и запросами к API
├── nginx/
│   └── Dockerfile            # Конфигурация Reverse Proxy (статика + проксирование /api/)
├── docker-compose.yml        # Оркестрация сервисов (db, redis, backend, nginx)
├── locustfile.py             # Сценарии нагрузочного тестирования (Locust)
└── .gitignore
```

---

## 🚀 Быстрый запуск через Docker Compose (Рекомендуемый)

Весь стек (PostgreSQL, Redis, FastAPI на 4 воркерах, Nginx и Vue-фронтенд) поднимается одной командой.

### 1. Клонирование репозитория
```bash
git clone https://github.com/FilianoreBarrier/fast-delivery
cd fast-delivery
```

### 2. Настройка переменных окружения
Создайте файл `.env` в корне проекта (рядом с `docker-compose.yml`), а также `backend/.env`:
```env
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password@db:5432/postgres
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Сборка и запуск контейнеров
```bash
docker-compose up -d --build
```
*(При запуске контейнера `backend` миграции Alembic применяются автоматически).*

### 4. Доступ к сервисам
* **Веб-интерфейс (Vue 3 SPA):** `http://localhost`
* **Swagger UI (Документация API):** `http://localhost/docs` (или напрямую `http://localhost:8001/docs`)
* **ReDoc:** `http://localhost/redoc`
* **OpenAPI JSON:** `http://localhost/openapi.json`

---

## 🧪 Тестирование и CI/CD

### Интеграционные тесты (Pytest)
В проекте реализовано покрытие репозиториев, сервисов, авторизации и работы с Redis с использованием изолированных фикстур. При каждом `push` в ветку `master` автоматически запускается пайплайн **GitHub Actions**.

Локальный запуск тестов:
```bash
cd backend
pytest -v
```

### Нагрузочное тестирование и оптимизация (Locust)
Было проведено нагрузочное и стресс-тестирование (`locustfile.py`) со смешанным профилем нагрузки (чтение каталога + регистрация пользователей с хэшированием паролей).

**Результаты оптимизации при 100 одновременных виртуальных пользователях (100 VU):**

| Метрика | До оптимизации (1 worker, sync bcrypt) | После оптимизации (4 workers, async threadpool, DB pool) | Улучшение |
| :--- | :--- | :--- | :--- |
| **Пропускная способность (RPS)** | 15 – 18 req/s | **62 – 65 req/s** | **×3.8 раза** |
| **Медианное время ответа (p50)** | 3 500 – 5 000 мс | **~20 мс** | **×200 раз** |
| **95-й перцентиль (p95)** | 12 000 – 14 000 мс | **300 – 400 мс** | **×30 раз** |
| **Процент ошибок (Failures)** | 0% | **0%** | Стабильно |

* **Точка отказа (Break-Point / Stress Test):** система стабильно выдерживает до **~2 300 одновременных активных пользователей** на одной локальной ноде без деградации при рабочей нагрузке.

**Запуск нагрузочного теста локально:**
```bash
pip install locust
locust -f locustfile.py --host=http://localhost
# Веб-интерфейс Locust откроется по адресу http://localhost:8089
```
