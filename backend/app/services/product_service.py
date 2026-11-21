from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.exc import IntegrityError

from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.product import ProductResponse, ProductListResponse, ProductCreate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    async def get_all_products(self) -> ProductListResponse:
        products = await self.product_repository.get_all()
        return ProductListResponse.model_validate({"products": products, "total": len(products)})

    async def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Product with id {product_id} not found'
            )
        return ProductResponse.model_validate(product)

    async def get_product_by_category(self, category_id:int) -> ProductListResponse:
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        products = await self.product_repository.get_by_category(category_id)
        return ProductListResponse.model_validate({"products": products, "total": len(products)})


    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        category = await self.category_repository.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Category with id {product_data.category_id} does not exist'
            )
        existing = await self.product_repository.get_by_name(product_data.name)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with '{product_data.name}' already exists"
            )
        product = await self.product_repository.create(product_data)
        return ProductResponse.model_validate(product)

    async def delete_product(self, product_id: int) -> None:
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        try:
            await self.product_repository.delete(product_id)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete product because it is referenced in existing orders",
            )


    async def get_batch_products_by_ids(self, ids: List[int]) -> List[ProductResponse]:
        if not ids:
            return []
        products = await self.product_repository.get_multiple_by_ids(ids)
        return [ProductResponse.model_validate(prod) for prod in products]
