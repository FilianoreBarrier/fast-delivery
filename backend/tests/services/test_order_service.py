import pytest
from fastapi import HTTPException
from app.core.redis import get_redis

@pytest.mark.asyncio
async def test_create_order_empty_cart(order_service):
    """Тест: сервис должен выбросить 400, если корзина пуста"""

    redis = await get_redis()
    await redis.delete("cart:user:1")

    with pytest.raises(HTTPException) as exc_info:
        await order_service.create_order_from_cart(user_id=1, redis= redis)

    assert exc_info.value.status_code == 400
    assert "empty cart" in exc_info.value.detail
