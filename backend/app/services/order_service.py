from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.exceptions import raise_user_not_found, raise_order_not_found
from app.models.order.order import OrderStatus
from app.models.order.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.cart_service import CartService


class OrderService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repository = OrderRepository(db)
        self.product_repository = ProductRepository(db)
        self.user_repository = UserRepository(db)

    async def get_orders(self, user_id: int) -> list[OrderResponse]:
        if not await self.user_repository.get_by_id(user_id):
            raise_user_not_found(user_id)
        orders = await self.order_repository.get_by_user_id(user_id)
        return [OrderResponse.model_validate(order) for order in orders]

    async def status_order_update(self, id: int, order_update: OrderStatusUpdate):
        order = await self.order_repository.get_by_id(id)
        if not order:
            raise_order_not_found(id)

        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify a cancelled order",
            )
        try:
            updated = await self.order_repository.status_update(id, order_update)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        return updated

    async def create_order_from_cart(self, user_id: int, redis:Redis) -> OrderResponse:
        cart_service = CartService(self.db, redis)
        cart_data = await cart_service.get_raw_cart(user_id)
        if not cart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create an order from an empty cart",
            )

        if not await self.user_repository.get_by_id(user_id):
            raise_user_not_found(user_id)

        # Один запрос вместо N+1
        products = {
            p.id: p
            for p in await self.product_repository.get_multiple_by_ids(list(cart_data))
        }

        total_price = 0.0
        items: list[OrderItem] = []
        for product_id, quantity in cart_data.items():
            if quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product quantity must be greater than zero",
                )
            product = products.get(product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {product_id} not found",
                )
            total_price += float(product.price) * quantity
            items.append(
                OrderItem(product_id=product.id, quantity=quantity, price=float(product.price))
            )

        # Заказ и позиции сохраняются одной транзакцией: репозитории только flush,
        # единственный commit — здесь.
        try:
            new_order = await self.order_repository.create(
                order_data=OrderCreate(user_id=user_id),
                total_price=round(total_price, 2),
            )
            for item in items:
                item.order_id = new_order.id
            await self.order_repository.create_items(items)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        # Корзину чистим только после успешного commit
        await cart_service.clear_cart(user_id)

        full_order = await self.order_repository.get_order_with_items(new_order.id)
        return OrderResponse.model_validate(full_order)
