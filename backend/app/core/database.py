from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug
)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

async def init_db():
    from app.models.user import User
    from app.models.order import Order
    from app.models.user import TokenBlackList
    from app.models.order import OrderItem
    from app.models.product import Product
    from app.models.product import Category

    # Создание таблиц в асинхронном режиме через engine.begin()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
