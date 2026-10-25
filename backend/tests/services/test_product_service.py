from unittest.mock import AsyncMock
import pytest
from fastapi import HTTPException
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate
from app.models.product import Product

@pytest.mark.asyncio
async def test_create_product_category_not_found():
    """Тест: сервис должен выбросить 404, если категории не существует"""
    mock_db = AsyncMock()
    service = ProductService(db=mock_db)

    service.category_repository.get_by_id = AsyncMock(return_value=None)

    # 4. Готовим тестовые данные
    product_data = ProductCreate(
        name="Телефон",
        price=50000.0,
        category_id=999, # Несуществующий ID
        description="Крутой смартфон",
        image_url=None
    )

    # 5. Проверяем, что сервис выбрасывает HTTPException с кодом 404
    with pytest.raises(HTTPException) as exc_info:
        await service.create_product(product_data)

    assert exc_info.value.status_code == 404
    assert "does not exist" in exc_info.value.detail
