import pytest
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user_success(user_repo):
    """Тест успешного создания пользователя в базе данных"""

    # 1. Готовим тестовые входные данные через схему Pydantic
    test_user_data = UserCreate(
        username="test_buyer_1",
        email="buyer1@example.com",
        full_name="Иван Иванов",
        role = "buyer",
        password="test123442"
    )

    # 2. Вызываем метод вашего UserRepository
    new_user = await user_repo.create(
        user_data=test_user_data,
        hashed_password="mocked_bcrypt_hash_xyz_123",
        role="buyer"
    )

    # 3. Проверяем результат (Утверждения / Asserts)
    assert new_user.id is not None, "База данных должна была присвоить пользователю ID"
    assert new_user.username == "test_buyer_1"
    assert new_user.email == "buyer1@example.com"
    assert new_user.full_name == "Иван Иванов"
    assert new_user.role == "buyer"
    assert new_user.is_active is True, "Новый пользователь по умолчанию должен быть активен"


@pytest.mark.asyncio
async def test_get_by_email_success(user_repo):
    """Тест успешного поиска пользователя по email"""

    # 1. Сначала создаем пользователя в базе, чтобы было кого искать
    user_data = UserCreate(
        username="test_search_user",
        email="search@example.com",
        full_name="Петр Петров",
        role = "buyer",
        password="test123442"
    )
    created_user = await user_repo.create(
        user_data=user_data,
        hashed_password="some_hash",
        role="seller"
    )

    # 2. Вызываем метод поиска по email
    found_user = await user_repo.get_by_email(email="search@example.com")

    # 3. Проверяем, что мы нашли именно того, кого создали
    assert found_user is not None, "Пользователь должен быть найден в базе"
    assert found_user.id == created_user.id
    assert found_user.username == "test_search_user"
