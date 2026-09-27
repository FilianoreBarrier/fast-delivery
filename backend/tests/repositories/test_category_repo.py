import pytest
from app.schemas.category import CategoryCreate

@pytest.mark.asyncio
async def test_create_category(category_repo):
    test_category_data = CategoryCreate(
        name='Electronic',
        slug="computer.slug"
    )
    new_category = await category_repo.create(
        category_data = test_category_data
    )

    assert new_category.id is not None, "База данных должна была присвоить ID категории."
    assert new_category.name == 'Electronic'
    assert new_category.slug == 'computer.slug'

@pytest.mark.asyncio
async def test_get_by_id(category_repo):
    test_category_data = CategoryCreate(
        name='Electronic',
        slug="electronic"
    )
    created_category = await category_repo.create(category_data = test_category_data)
    found_category = await category_repo.get_by_id(created_category.id)

    assert found_category is not None, "Категория должна быть найдена в базе"
    assert found_category.id == created_category.id
    assert found_category.slug == "electronic"
    assert found_category.name == "Electronic"

@pytest.mark.asyncio
async def test_get_by_slug(category_repo):
    test_category_data = CategoryCreate(
        name = "IPhone",
        slug = 'phones'
    )
    created_category = await category_repo.create(category_data = test_category_data)
    found_category = await category_repo.get_by_slug('phones')

    assert found_category is not None
    assert found_category.id == created_category.id
    assert found_category.slug == "phones"
    assert found_category.name == "IPhone"



    # async def get_by_slug(self, slug: str) -> Category | None:
    #     stmt = select(Category).where(Category.slug == slug)
    #     result = await self.db.scalar(stmt)
    #     return result
