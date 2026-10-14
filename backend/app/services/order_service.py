from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository

from app.schemas.order import OrderCreate, OrderResponse
from app.models.order.order_item import OrderItem


class OrderService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repository = OrderRepository(db)
        self.product_repository = ProductRepository(db)
        self.user_repository = UserRepository(db)

    async def create_order_from_cart(
        self,
        user_id: int,
        cart_data: Dict[int, int]
    ) -> OrderResponse:

        if not cart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create an order from an empty cart"
            )

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        calculated_total_price = 0.0
        order_items_to_save = []

        for product_id, quantity in cart_data.items():

            if quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product quantity must be greater than zero"
                )

            product = await self.product_repository.get_by_id(product_id)

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {product_id} not found"
                )

            item_price = float(product.price)

            calculated_total_price += item_price * quantity

            order_items_to_save.append(
                OrderItem(
                    product_id=product.id,
                    quantity=quantity,
                    price=item_price
                )
            )

        try:
            async with self.db.begin():

                order_create_schema = OrderCreate(
                    user_id=user_id
                )

                new_order = await self.order_repository.create(
                    order_data=order_create_schema,
                    total_price=calculated_total_price
                )

                for item in order_items_to_save:
                    item.order_id = new_order.id

                await self.order_repository.create_items(
                    order_items_to_save
                )

        except Exception:
            raise

        full_order = await self.order_repository.get_order_with_items(
            new_order.id
        )

        return OrderResponse.model_validate(full_order)
