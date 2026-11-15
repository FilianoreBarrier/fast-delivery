from sqlalchemy.orm import joinedload

from app.models.product import Product
from app.schemas.product import ProductCreate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db =db

    async def get_all(self) -> list[Product]:
            stmt = select(Product).options(joinedload(Product.category))
            result = await self.db.scalars(stmt)
            return list(result.all())

    async def get_by_id(self, id: int) -> Product | None:
        # category подгружаем сразу: ProductResponse её требует,
        # а ленивая загрузка в async падает с MissingGreenlet
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id == id)
            .execution_options(populate_existing=True)
        )
        return await self.db.scalar(stmt)

    async def get_by_category(self, category_id: int) -> list[Product]:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.category_id == category_id)
        )
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, product_data: ProductCreate) -> Product:
        db_product = Product(**product_data.model_dump())
        self.db.add(db_product)
        await self.db.commit()
        # перечитываем вместе с category, чтобы ответ можно было сериализовать
        return await self.get_by_id(db_product.id)

    async def get_multiple_by_ids(self, product_ids: list[int]) -> list[Product]:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id.in_(product_ids))
        )
        result = await self.db.scalars(stmt)
        return list(result.all())
