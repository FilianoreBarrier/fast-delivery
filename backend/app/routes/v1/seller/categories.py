from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.services.category_service import CategoryService
from app.schemas.category import CategoryResponse,CategoryCreate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_categories(db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return await service.get_all_categories()


@router.get(
    "/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK
)
async def get_category_by_id(
    category_id: int,
    db: AsyncSession = Depends(get_db)):

    service = CategoryService(db)
    return await service.get_category_by_id(category_id)

@router.post(
        '/', response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
        )
async def create_category(
    category_data:CategoryCreate,
    db:AsyncSession = Depends(get_db)):

    service = CategoryService(db)
    return await service.create_category(category_data)
