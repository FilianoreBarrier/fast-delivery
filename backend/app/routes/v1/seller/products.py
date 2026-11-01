from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductListResponse, ProductResponse, ProductCreate


router = APIRouter(prefix="/products", tags=['products'])

@router.get("/", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_products(db:AsyncSession = Depends(get_db)):
        service = ProductService(db)
        return await service.get_all_products()

@router.post("/", response_model=ProductResponse,status_code=status.HTTP_201_CREATED)
async def create_product(
        product_data:ProductCreate,
        db:AsyncSession = Depends(get_db)):

        service = ProductService(db)
        return await service.create_product(product_data)

@router.get("/{product_id}", response_model=ProductResponse,status_code=status.HTTP_200_OK)
async def get_product_by_id(
        product_id:int,
        db:AsyncSession = Depends(get_db)):

        service = ProductService(db)
        return await service.get_product_by_id(product_id)

@router.get(
    "/category/{category_id}",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.get_product_by_category(category_id)
