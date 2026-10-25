import pytest
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_create_order_empty_cart(order_service):
    """Тест: сервис должен выбросить 400, если корзина пуста"""

    # Вызываем метод с пустым словарем cart_data
    with pytest.raises(HTTPException) as exc_info:
        await order_service.create_order_from_cart(user_id=1, cart_data={})

    assert exc_info.value.status_code == 400
    assert "empty cart" in exc_info.value.detail
