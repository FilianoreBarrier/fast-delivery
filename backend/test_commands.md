# Руководство по тестированию FastDelivery API в Postman

## 1. Подготовка

### 1.1 Запуск окружения

| Режим | Base URL |
|---|---|
| Локально (`python run.py`) | `http://127.0.0.1:8012` |
| Docker (`docker compose up`) | `http://127.0.0.1:8001` |

Должны работать PostgreSQL (с применёнными миграциями) и Redis. Быстрая проверка: `GET {{base_url}}/` вернёт `{"message": "FastDelivery API работает!", "docs": "/docs"}`.

### 1.2 Импорт коллекции

1. Postman → **Import** → выберите `docs/FastDelivery.postman_collection.json`.
2. Откройте коллекцию → вкладка **Variables** и при необходимости поправьте `base_url`.
3. Остальные переменные (`token_buyer`, `token_seller`, `category_id`, `product_id`, …) заполняются автоматически тест-скриптами.

### 1.3 Переменные

| Переменная | Назначение |
|---|---|
| `base_url` | Адрес сервера (без `/api/v1`) |
| `api` | Префикс, по умолчанию `/api/v1` |
| `suffix` | Случайный суффикс, чтобы имена товаров/категорий не конфликтовали между прогонами |
| `buyer_email`, `buyer_password` | Данные покупателя |
| `seller_email`, `seller_password` | Данные продавца |
| `token_buyer`, `token_seller` | JWT (сохраняются после логина) |
| `buyer_id`, `category_id`, `product_id`, `order_id` | ID созданных сущностей |

## 2. Получение продавца (обязательный ручной шаг)

Регистрация всегда создаёт роль `buyer` (поле `role` в теле игнорируется сервисом). Чтобы протестировать seller-эндпоинты:

1. Выполните запрос **0. Setup → Register seller candidate**.
2. Повысьте роль в БД:

```bash
# Docker
docker exec -it fast_delivery_db psql -U postgres -d postgres \
  -c "UPDATE users SET role = 'SELLER' WHERE email = 'seller@example.com';"
```

(в БД enum хранится в верхнем регистре: `BUYER` / `SELLER`).
3. Продолжайте с папки **1. Auth**.

## 3. Порядок прогона

Запросы в коллекции расположены в нужном порядке, многие зависят от переменных, сохранённых предыдущими. Можно запускать через **Collection Runner** (Run collection) после выполнения шага из раздела 2. Папку **0. Setup** запустите один раз заранее.

| Папка | Что проверяет |
|---|---|
| 0. Setup | Доступность API, регистрация buyer и seller-кандидата |
| 1. Auth & Users | Логин, `/users/me`, права доступа, 401/403/404 |
| 2. Categories | Создание/чтение категорий, RBAC, дубликаты |
| 3. Products | Создание/чтение товаров, валидация, 404/409/422 |
| 4. Cart | Корзина в Redis: добавление, накопление, обновление, удаление |
| 5. Orders | Заказ из пустой корзины, успешный заказ, очистка корзины, история |
| 6. Logout | Выход и проверка чёрного списка токенов |

## 4. Описание сценариев и ожидаемые результаты

Авторизованные запросы отправляют заголовок `Authorization: Bearer {{token_*}}`.

### 4.1 Auth & Users

| Запрос | Ожидание |
|---|---|
| `POST /auth/register` (валидные данные) | **201**, `role: "buyer"`, `is_active: true`, пароля в ответе нет |
| `POST /auth/register` (повтор того же email) | **409** `The email is already taken.` |
| `POST /auth/register` (повтор username) | **409** `The username is already taken` |
| `POST /auth/register` (пароль < 8 символов / невалидный email / username < 3) | **422** |
| `POST /auth/login` | **200**, `access_token`, `user` |
| `POST /auth/login` (неверный пароль) | **401** `Incorrect email or password` |
| `GET /users/me` | **200**, данные текущего пользователя |
| `GET /users/me` без токена | **401** `Not authenticated` |
| `GET /users/me` с мусорным токеном | **401** `Could not validate credentials` |
| `GET /users/{id}` | **200**, только `id`, `username`, `full_name` (email не отдаётся) |
| `GET /users/999999` | **404** |
| `GET /auth/users-activity` (buyer) | **403** `Seller role required` |
| `GET /auth/users-activity` (seller) | **200**, массив пользователей |

### 4.2 Categories

Тело создания: `{"name": "Test Category", "slug": "test-category"}` (name и slug: 3–100 символов).

| Запрос | Ожидание |
|---|---|
| `POST /categories/` (buyer) | **403** |
| `POST /categories/` (seller) | **201**, возвращается `id` |
| `POST /categories/` (повтор slug) | **400** `Category with slug ... already exists.` |
| `POST /categories/` (name < 3 символов) | **422** |
| `GET /categories/` | **200**, массив (без токена) |
| `GET /categories/{id}` | **200** |
| `GET /categories/999999` | **404** |

### 4.3 Products

Тело создания:
```json
{
  "name": "Test Product",
  "description": "Описание",
  "price": 100,
  "category_id": 1,
  "image_url": null
}
```
(`name`: 5–200 символов, `price` > 0.)

| Запрос | Ожидание |
|---|---|
| `POST /products/` (buyer) | **403** |
| `POST /products/` (seller) | **201**, вложенный объект `category` |
| `POST /products/` (повтор name) | **409** |
| `POST /products/` (несуществующая категория) | **404** `... does not exist` |
| `POST /products/` (`price: 0` или короткое имя) | **422** |
| `GET /products/` | **200**, `{"products": [...], "total": N}` |
| `GET /products/{id}` | **200** |
| `GET /products/999999` | **404** |
| `GET /products/category/{category_id}` | **200**, список товаров категории |
| `GET /products/category/999999` | **404** |

### 4.4 Cart

Цена товара в сценарии — 100.

| Шаг | Запрос | Ожидание |
|---|---|---|
| 1 | `GET /cart/` | **200**, `items: []`, `total: 0`, `items_count: 0` |
| 2 | `POST /cart/add` `{"product_id": X, "quantity": 2}` | **200**, `items_count: 2`, `total: 200` |
| 3 | Повторить `add` с `quantity: 1` | количество **суммируется**: `items_count: 3`, `total: 300` |
| 4 | `PUT /cart/update` `{"product_id": X, "quantity": 5}` | количество **заменяется**: `items_count: 5`, `total: 500` |
| 5 | `PUT /cart/update` для товара, которого нет в корзине | **404** `not found in cart` |
| 6 | `POST /cart/add` с несуществующим `product_id` | **404** |
| 7 | `POST /cart/add` с `quantity: 0` или отрицательным | **422** |
| 8 | `DELETE /cart/remove/{X}` | **200**, корзина пуста |
| 9 | Любой `/cart/*` без токена | **401** |

Проверка Redis (необязательно):
```bash
docker exec -it fast_delivery_redis redis-cli HGETALL cart:user:<buyer_id>
docker exec -it fast_delivery_redis redis-cli TTL cart:user:<buyer_id>   # ≈ 604800
```

### 4.5 Orders

| Шаг | Запрос | Ожидание |
|---|---|---|
| 1 | `POST /orders/` при пустой корзине | **400** `Cannot create an order from an empty cart` |
| 2 | `POST /cart/add` (product X, qty 2) | **200** |
| 3 | `POST /orders/` (тело не нужно) | **201**, `status: "Unpaid"`, `total_price: 200`, `order_items` с 1 позицией (`price` зафиксирована на момент заказа) |
| 4 | `GET /cart/` | корзина **пуста** (очищается после commit) |
| 5 | `GET /orders/` | **200**, в списке есть созданный заказ |
| 6 | `GET /orders/` без токена | **401** |

Каждый пользователь видит только свои заказы: для проверки изоляции зарегистрируйте второго покупателя, войдите и убедитесь, что его `GET /orders/` пуст.

### 4.6 Logout

| Запрос | Ожидание |
|---|---|
| `POST /auth/logout` | **200** `{"message": "Successfully logged out"}` |
| `GET /users/me` с тем же токеном | **401** `Token is blacklisted. Please log in again.` |
| `POST /auth/login` снова | новый токен работает |

> После logout `token_buyer` недействителен. При повторном прогоне коллекции заново выполните логин (он есть в папке 1).

## 5. Ручная настройка запросов (если без коллекции)

1. Создайте Environment с `base_url`, `token_buyer`, `token_seller`.
2. В тестах (вкладка **Tests**) запроса логина добавьте сохранение токена:
   ```js
   const j = pm.response.json();
   pm.environment.set("token_buyer", j.access_token);
   ```
3. В авторизованных запросах выберите **Authorization → Bearer Token** со значением `{{token_buyer}}`.
4. Для тел запросов: **Body → raw → JSON**.

## 6. Частые проблемы

| Симптом | Причина / решение |
|---|---|
| `307 Temporary Redirect` или потеря заголовка `Authorization` | Не указан завершающий `/` (`/products/`, `/categories/`, `/orders/`, `/cart/`). Используйте путь ровно как в документации |
| `401` на всех защищённых запросах | Токен истёк (по умолчанию 60 мин), в нём опечатка, или был выполнен logout |
| `403 Seller role required` | Не выполнено повышение роли в БД (раздел 2) или токен получен до него: залогиньтесь заново |
| `500` на `POST /categories/` | Категория с таким `name` уже существует (проверяется только `slug`) |
| `ConnectionError` / `500` на `/cart/*` | Не запущен Redis или неверный `REDIS_URL` |
| `connection refused` | Неверный порт: `8012` локально, `8001` в Docker |
| `alembic upgrade head` падает с `AttributeError: DATABASE_URL` | Задайте переменную окружения `DATABASE_URL` или исправьте `alembic/env.py`: `settings.database_url` (в `config.py` поле в нижнем регистре) |

## 7. Что API пока не умеет (не тестируется)

* Смена статуса заказа — сервис есть, маршрута нет.
* Смена пароля и обновление профиля — аналогично.
* Назначение роли `seller` — только через БД.
