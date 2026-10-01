from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse

class CategoryService:
    def __init__(self, db:AsyncSession):
        self.repository = CategoryRepository(db)

    async def get_all_categories(self) -> List[CategoryResponse]:
        categories = await self.repository.get_all()
        return [CategoryResponse.model_validate(cat) for cat in categories]

    async def get_category_by_id(self, category_id: int) -> CategoryResponse:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Category with id {category_id} not found.'
            )
        return CategoryResponse.model_validate(category)

    async def get_category_by_slug(self, slug: str) -> CategoryResponse:
        category = await self.repository.get_by_slug(slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Category with slug "{slug}" - not found.'
            )
        return CategoryResponse.model_validate(category)

    async def create_category(self, category_data:CategoryCreate) -> CategoryResponse:
        existing = await self.repository.get_by_slug(category_data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Category with slug "{category_data.slug}" already exists.'
            )
        category = await self.repository.create(category_data)
        return CategoryResponse.model_validate(category)
