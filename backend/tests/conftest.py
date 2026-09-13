from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import asyncio
from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


from app.core.config import settings
from app.core.database import Base

import app.models


TEST_DATABASE_URL = settings.test_database_url


# 1. Создаем асинхронный движок для тестовой базы данных
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# 2. Создаем фабрику асинхронных сессий для тестов
# Не забудьте добавить импорт async_sessionmaker в самый верх файла!
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False
)



# Обязательная фикстура, которая настраивает цикл событий (event loop) для pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Фикстура подготовки БД: создает таблицы перед тестами и удаляет их в самом конце
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Перед стартом ВСЕХ тестов: генерируем чистые таблицы в test_delivery_db
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # Здесь запускаются и выполняются все ваши файлы тестов

    # После окончания ВСЕХ тестов: полностью удаляем таблицы, очищая базу за собой
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Главная фикстура сессии: выдает каждому тесту изолированную транзакцию
@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        async with session.begin():  # Открываем транзакцию
            yield session
        # Как только конкретный тест завершился, контекст закрывается,
        # и SQLAlchemy принудительно делает ROLLBACK.
        # База данных снова идеально пустая и готова к следующему тесту!


# Фикстура-помощник для репозитория пользователей
@pytest.fixture(scope="function")
def user_repo(db_session: AsyncSession):
    from app.repositories.user_repository import UserRepository
    return UserRepository(db_session)
