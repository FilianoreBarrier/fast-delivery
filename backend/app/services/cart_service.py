from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Dict
from redis.asyncio import Redis

from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartResponse, CartItem, CartItemCreate, CartItemUpdate

class CartService:
    def __init__(self, db: AsyncSession, redis:Redis):
        self.product_repository = ProductRepository(db)
        self.redis = redis
        self.ttl = 60*60*24*7 #корзина хранится в redis 7 дней

    def _get_cart_key(self, user_id: int) -> str:
        """Формирует уникальный ключ корзины пользователя в Redis"""
        return f"cart:user:{user_id}"

    async def get_raw_cart(self, user_id: int) -> Dict[int, int]:
        """Копия корзины {product_id: quantity} из Redis для других сервисов"""
        raw_data = await self.redis.hgetall(self._get_cart_key(user_id))
        return {int(prod_id): int(qty) for prod_id, qty in raw_data.items()}

    async def clear_cart(self, user_id: int) -> None:
        """Полностью очищает корзину пользователя в Redis"""
        await self.redis.delete(self._get_cart_key(user_id))

    async def add_to_cart(self, user_id: int, item: CartItemCreate) -> CartResponse:
        """Добавляет товар в корзину покупателя или увеличивает его количество"""
        product = await self.product_repository.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found",
            )

        key = self._get_cart_key(user_id)
        await self.redis.hincrby(key, str(item.product_id), item.quantity)
        await self.redis.expire(key, self.ttl)
        return await self.get_cart(user_id)

    async def update_cart_item(self, user_id: int, item: CartItemUpdate) -> CartResponse:
        """Изменяет количество товара на конкретное новое значение"""
        key = self._get_cart_key(user_id)
        exists = await self.redis.hexists(key, str(item.product_id))
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found in cart",
            )

        product = await self.product_repository.get_by_id(item.product_id)
        if not product:
            await self.redis.hdel(key, str(item.product_id))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} no longer exists",
            )

        await self.redis.hset(key, str(item.product_id), item.quantity)
        await self.redis.expire(key, self.ttl)
        return await self.get_cart(user_id)

    async def remove_from_cart(self, user_id: int, product_id: int) -> CartResponse:
        """Полностью удаляет товар из корзины пользователя"""
        key = self._get_cart_key(user_id)
        await self.redis.hdel(key, str(product_id))
        return await self.get_cart(user_id)

    async def get_cart(self, user_id: int) -> CartResponse:
        """Собирает CartResponse, обогащая id товаров актуальными данными из БД"""
        key = self._get_cart_key(user_id)
        cart = await self.get_raw_cart(user_id)

        cart_items: list[CartItem] = []
        total_price = 0.0
        total_items_count = 0

        for product_id, quantity in cart.items():
            product = await self.product_repository.get_by_id(product_id)

            if not product:
                await self.redis.hdel(key, str(product_id))
                continue

            subtotal = round(product.price * quantity, 2)
            total_price = round(total_price + subtotal, 2)
            total_items_count += quantity

            cart_items.append(
                CartItem(
                    product_id=product.id,
                    quantity=quantity,
                    name=product.name,
                    price=product.price,
                    subtotal=subtotal,
                    image_url=product.image_url,
                )
            )

        return CartResponse(
            items=cart_items,
            total=total_price,
            items_count=total_items_count,
        )
