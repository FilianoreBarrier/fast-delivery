import pytest
from app.schemas.user import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_create_user(user_repo):
    """Тест успешного создания пользователя в базе данных"""

    test_user_data = UserCreate(
        username="test_buyer_1",
        email="buyer1@example.com",
        full_name="Иван Иванов",
        role = "buyer",
        password="test123442"
    )

    new_user = await user_repo.create(
        user_data=test_user_data,
        hashed_password="mocked_bcrypt_hash_xyz_123",
        role="buyer"
    )

    assert new_user.id is not None, "База данных должна была присвоить пользователю ID"
    assert new_user.username == "test_buyer_1"
    assert new_user.email == "buyer1@example.com"
    assert new_user.full_name == "Иван Иванов"
    assert new_user.role == "buyer"
    assert new_user.is_active is True, "Новый пользователь по умолчанию должен быть активен"


@pytest.mark.asyncio
async def test_get_by_email(user_repo):
    """Тест успешного поиска пользователя по email"""
    test_user_data = UserCreate(
        username="test_search_user",
        email="search@example.com",
        full_name="Петр Петров",
        role = "buyer",
        password="test123442"
    )
    created_user = await user_repo.create(
        user_data=test_user_data,
        hashed_password="some_hash",
        role="seller"
    )

    found_user = await user_repo.get_by_email(email="search@example.com")

    assert found_user is not None, "Пользователь должен быть найден в базе"
    assert found_user.id == created_user.id
    assert found_user.username == "test_search_user"
    assert found_user.email == created_user.email

@pytest.mark.asyncio
async def test_get_all(user_repo):
    tud_1 = UserCreate(           #tud - test_user_data
        username="test_get_all_1",
        email="search.asf@example.com",
        full_name="Петр Петров",
        role = "buyer",
        password="test123442"
    )
    tud_2 = UserCreate(
        username="test_get_all_2",
        email="search.test@example.com",
        full_name="Петр Иванов",
        role = "buyer",
        password="testsf442"
    )
    cu_1 = await user_repo.create(   #cu - created_user
    user_data=tud_1,
    hashed_password="some_hash",
    role = "buyer"
    )

    cu_2 = await user_repo.create(   #cu - created_user
        user_data=tud_2,
        hashed_password="some_hash",
        role = "seller"
    )

    users = await user_repo.get_all()

    user_ids = [user.id for user in users]

    assert cu_1.id in user_ids
    assert cu_2.id in user_ids

@pytest.mark.asyncio
async def test_get_by_id(user_repo):
    test_user_data = UserCreate(
        username="test_buyer_3",
        email="buyer4@example.com",
        full_name="Иван Иванов",
        role = "buyer",
        password="test123442"
    )
    new_user = await user_repo.create(
        user_data=test_user_data,
        hashed_password="mocked_bcrypt_hash_xyz_123",
        role="buyer"
    )
    found_user = await user_repo.get_by_id(new_user.id)

    assert found_user is not None, "Пользователь должен быть найден в базе"
    assert found_user.id == new_user.id
    assert found_user.username == "test_buyer_3"
    assert found_user.email == "buyer4@example.com"

@pytest.mark.asyncio
async def test_get_by_username(user_repo):
    test_user_data = UserCreate(
        username="test_seller_3",
        email="seller4@example.com",
        full_name="Иван Иванов",
        role = "buyer",
        password="test123442"
    )
    new_user = await user_repo.create(
        user_data=test_user_data,
        hashed_password="mocked_bcrypt_hash_xyz_123",
        role="seller"
    )
    found_user = await user_repo.get_by_username(new_user.username)

    assert found_user is not None, "Пользователь должен быть найден в базе"
    assert found_user.id == new_user.id
    assert found_user.username == "test_seller_3"
    assert found_user.email == "seller4@example.com"

@pytest.mark.asyncio
async def test_update(user_repo):
    tud = UserCreate(
            username="test_buyer_10",
            email="love4u@example.com",
            full_name="Николай Румянцев",
            role = "buyer",
            password="sf12hgd3442"
        )
    new_user = await user_repo.create(
        user_data=tud,
        hashed_password="mocked_bcrypt_hash_xyz_123",
        role="buyer"
    )
    update_user_data = UserUpdate(
        full_name= "Валентин Штык",
        email="lovebackend@example.com"

    )
    user_update = await user_repo.update(new_user.id, update_user_data)
    assert user_update.id is not None, "База данных должна была присвоить пользователю ID"
    assert user_update.id == new_user.id
    assert user_update.username == "test_buyer_10"
    assert user_update.email == "lovebackend@example.com"
    assert user_update.full_name == "Валентин Штык"


@pytest.mark.asyncio
async def test_update_password(user_repo):
    old_hash = 'sdkgoxcbo.sdohsdhofocn.xzcbankxoobfd'
    new_hash = "kesfeskfk.osajkvd0odv.sdvlasld"

    tud = UserCreate(
                username="test_buyer_11",
                email="love1u@example.com",
                full_name="Николай Румянцев",
                role = "buyer",
                password="sx52sfhgd3442"
            )

    new_user = await user_repo.create(
        user_data=tud,
        hashed_password=old_hash,
        role="buyer"
        )

    changed_user = await user_repo.update_password(new_user.id, new_hash
    )

    assert changed_user is not None
    assert changed_user.id == new_user.id
    assert changed_user.hashed_password == new_hash
    assert changed_user.hashed_password != old_hash

@pytest.mark.asyncio
async def test_get_multiple_by_ids(user_repo):
    tud_1 = UserCreate(
        username="test_multiple_1",
        email="multiple1@example.com",
        full_name="Петр Петров",
        role="buyer",
        password="tasdgest123"
    )

    tud_2 = UserCreate(
        username="test_multiple_2",
        email="multiple2@example.com",
        full_name="Иван Иванов",
        role="seller",
        password="tsetest456"
    )

    created_user_1 = await user_repo.create(
        user_data=tud_1,
        hashed_password="hash_1",
        role="buyer"
    )

    created_user_2 = await user_repo.create(
        user_data=tud_2,
        hashed_password="hash_2",
        role="seller"
    )

    users = await user_repo.get_multiple_by_ids(
        [created_user_1.id, created_user_2.id]
    )

    assert len(users) == 2
    assert created_user_1.id in [user.id for user in users]
    assert created_user_2.id in [user.id for user in users]
