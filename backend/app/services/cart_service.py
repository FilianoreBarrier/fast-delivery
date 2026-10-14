from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Dict
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartResponse, CartItem, CartItemCreate, CartItemUpdate

class CartService:
    def __init__(self, db:AsyncSession):
        self.product_repository = ProductRepository(db)

    async def add_to_cart(
            self,
            cart_data: Dict[int,int],
            item: CartItemCreate
    ) -> Dict[int,int]:
        product = await self.product_repository.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found",
            )
        if item.product_id in cart_data:
            cart_data[item.product_id] += item.quantity
        else:
            cart_data[item.product_id] = item.quantity

        return cart_data

    async def update_cart_item(
            self,
            cart_data:Dict[int,int],
            item: CartItemUpdate
    ) -> Dict[int,int]:
        if item.product_id not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found in cart",
            )
        cart_data[item.product_id] = item.quantity
        return cart_data
