from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Dict
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartResponse, CartItem, CartItemCreate, CartItemUpdate

class CartService:
    # Временное хранилище для эмуляции Redis: {user_id: {product_id: quantity}}
    _storage: Dict[int, Dict[int, int]] = {}

    def __init__(self, db: AsyncSession):
        self.product_repository = ProductRepository(db)

    def _get_user_cart(self, user_id: int) -> Dict[int, int]:
        """Внутренний метод для получения или инициализации корзины пользователя"""
        if user_id not in self._storage:
            self._storage[user_id] = {}
        return self._storage[user_id]

    async def add_to_cart(self, user_id: int, item: CartItemCreate) -> CartResponse:
        """Добавляет товар в корзину покупателя или увеличивает его количество"""
        product = await self.product_repository.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found",
            )

        cart = self._get_user_cart(user_id)

        if item.product_id in cart:
            cart[item.product_id] += item.quantity
        else:
            cart[item.product_id] = item.quantity

        return await self.get_cart(user_id)

    async def update_cart_item(self, user_id: int, item: CartItemUpdate) -> CartResponse:
        """Изменяет количество товара на конкретное новое значение"""
        cart = self._get_user_cart(user_id)
        if item.product_id not in cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found in cart",
            )
        product = await self.product_repository.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} no longer exists",
            )
        cart[item.product_id] = item.quantity
        return await self.get_cart(user_id)

    async def remove_from_cart(self, user_id: int, product_id: int) -> CartResponse:
        """Полностью удаляет товар из корзины пользователя"""
        cart = self._get_user_cart(user_id)

        if product_id in cart:
            del cart[product_id]

        return await self.get_cart(user_id)

    async def get_cart(self, user_id: int) -> CartResponse:
        """Собирает CartResponse, обогащая id товаров актуальными данными из БД"""
        cart = self._get_user_cart(user_id)

        cart_items: list[CartItem] = []
        total_price = 0.0
        total_items_count = 0

        for product_id, quantity in list(cart.items()):
            product = await self.product_repository.get_by_id(product_id)

            if not product:
                del cart[product_id]
                continue

            subtotal = product.price * quantity
            total_price += subtotal
            total_items_count += quantity

            cart_items.append(
                CartItem(
                    product_id=product.id,
                    quantity=quantity,
                    name=product.name,
                    price=product.price,
                    subtotal=total_price,  # Считаем промежуточный итог для позиции
                    image_url=product.image_url
                )
            )

        return CartResponse(
            items=cart_items,
            total=total_price,
            items_count=total_items_count
        )
