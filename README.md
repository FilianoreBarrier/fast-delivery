# FastDelivery Backend

Асинхронный REST API сервис для платформы доставки и электронной коммерции, разработанный на базе **FastAPI** и **PostgreSQL**.

## ✨ Основной функционал

* **Аутентификация и безопасность:**
  * Регистрация и авторизация пользователей с использованием **JWT (JSON Web Tokens)**.
  * Хэширование паролей.
  * Система инвалидации токенов при выходе из аккаунта (Token Blacklist).
  * Ролевая модель доступа (`buyer`, `seller`).
* **Каталог и товары:**
  * Управление карточками товаров и категориями.
  * Валидация входящих и исходящих данных через **Pydantic v2**.
* **Корзина покупок:**
  * Добавление, обновление количества и удаление товаров в привязке к сессии авторизованного пользователя.
  * Динамический расчет стоимости корзины на основе актуальных цен из базы данных.
* **Управление заказами:**
  * Атомарное оформление заказа из корзины в рамках единой транзакции БД.
  * Автоматическая очистка корзины после успешного оформления заказа.
  * Просмотр истории заказов пользователя с подгрузкой всех позиций (`selectinload`).
  * Управление статусами заказа (`Unpaid`, `Paid`, `Processing`, `Shipped`, `Delivered`, `Cancelled`).

---

## 🛠 Технологический стек

* **Язык:** Python 3.11+
* **Веб-фреймворк:** FastAPI
* **База данных:** PostgreSQL
* **ORM и драйвер:** SQLAlchemy 2.0 (Async), `asyncpg`
* **Миграции БД:** Alembic
* **Валидация:** Pydantic v2
* **Аутентификация:** PyJWT, Passlib / Bcrypt
* **Тестирование:** Pytest

---

## 📂 Структура проекта

```text
fast-delivery/
├── backend/
│   ├── alembic/              # Миграции базы данных
│   ├── app/
│   │   ├── core/             # Конфигурация, настройки БД, безопасность и исключения
│   │   ├── models/           # ORM-модели SQLAlchemy (User, Product, Order, TokenBlackList)
│   │   ├── repositories/     # Слой доступа к данным (CRUD и сложные SQL-запросы)
│   │   ├── routes/           # Эндпоинты API (версионирование v1)
│   │   ├── schemas/          # Pydantic-схемы для валидации запросов и ответов
│   │   └── services/         # Бизнес-логика приложения
│   └── main.py               # Точка входа в приложение
└── .gitignore
```

---

## ⚙️ Установка и локальный запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com
cd fast-delivery/backend
```

### 2. Создание и активация виртуального окружения
```bash
# Для Windows
python -m venv venv
venv\Scripts\activate

# Для Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл `.env` в директории `backend/` и заполните его по следующему шаблону:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fast_delivery_db
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Применение миграций базы данных
```bash
alembic upgrade head
```

### 6. Запуск сервера
```bash
uvicorn main:app --reload --port 8012
```

---

## 📖 Документация API

После запуска сервера интерактивная документация Swagger UI и спецификация OpenAPI доступны по следующим адресам:

* **Swagger UI:** `http://127.0.0`
* **ReDoc:** `http://127.0.0`
* **OpenAPI JSON:** `http://127.0.0`
