from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base

import app.models  # noqa: F401

# Цикл событий задаётся в pytest.ini (asyncio_default_*_loop_scope = session),
# самописная фикстура event_loop больше не нужна.

test_engine = create_async_engine(settings.test_database_url, echo=False)

TestingSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
    # Репозитории делают commit, поэтому после каждого теста чистим таблицы,
    # чтобы тесты не зависели друг от друга.
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture(scope="function")
def user_repo(db_session: AsyncSession):
    from app.repositories.user_repository import UserRepository
    return UserRepository(db_session)


@pytest.fixture(scope="function")
def category_repo(db_session: AsyncSession):
    from app.repositories.category_repository import CategoryRepository
    return CategoryRepository(db_session)


@pytest.fixture(scope="function")
def product_repo(db_session: AsyncSession):
    from app.repositories.product_repository import ProductRepository
    return ProductRepository(db_session)


@pytest.fixture(scope="function")
def order_repo(db_session: AsyncSession):
    from app.repositories.order_repository import OrderRepository
    return OrderRepository(db_session)


@pytest.fixture(scope="function")
def token_repo(db_session: AsyncSession):
    from app.repositories.token_repository import TokenRepository
    return TokenRepository(db_session)


@pytest.fixture(scope="function")
def order_service(db_session: AsyncSession):
    from app.services.order_service import OrderService
    return OrderService(db_session)
