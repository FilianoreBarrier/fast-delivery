from app.models.product.category import Category
from app.schemas.category import CategoryCreate
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Category]:
        stmt = select(Category).options(selectinload(Category.products))
        result = await self.db.scalars(stmt)
        return list(result.all())


    async def get_by_id(self, id: int) -> Category | None:
        return await self.db.get(Category, id)

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        result = await self.db.scalar(stmt)
        return result

    async def create(self, category_data: CategoryCreate) -> Category:
        db_category = Category(**category_data.model_dump())
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category
