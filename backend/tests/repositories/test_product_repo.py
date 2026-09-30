import pytest
from app.schemas.product import ProductCreate
from app.schemas.category import CategoryCreate

@pytest.mark.asyncio
async def test_get_all(product_repo,category_repo):
        test_category_data = CategoryCreate(
                name='Books',
                slug="books"
            )
        new_category = await category_repo.create(
                category_data = test_category_data
            )

        tpd_1 = ProductCreate(   #tpd - test_product_data
            name = "Fairy Tail 2",
            description="This is fantastic",
            price = 100,
            category_id=new_category.id,
            image_url=None
        )
        tpd_2 = ProductCreate(
                name = "Lord of the lost lands",
                description="This is a book",
                price = 300,
                category_id=new_category.id,
                image_url=None
            )

        cr_p1 = await product_repo.create(  #created_product - cr_p
            product_data = tpd_1
        )
        cr_p2 = await product_repo.create(
            product_data = tpd_2
        )

        products = await product_repo.get_all()

        products_ids = [product.id for product in products]

        assert cr_p1.id in products_ids
        assert cr_p2.id in products_ids

@pytest.mark.asyncio
async def test_get_by_id(product_repo,category_repo):
    tcd = CategoryCreate(   #test_category_data
            name='Computers',
            slug="computers"
         )
    new_category = await category_repo.create(
            category_data = tcd
        )
    test_product_data = ProductCreate(
        name = "Lenovo Smart 14",
        description="This is PC with Intel i5-13000k",
        price = 750,
        category_id=new_category.id,
        image_url=None
    )
    new_product = await product_repo.create(
            product_data = test_product_data
        )

    found_product = await product_repo.get_by_id(
        id = new_product.id
    )
    assert found_product.id is not None,"База должен быть найден в базе "
    assert found_product.id == new_product.id
    assert found_product.name == new_product.name
    assert found_product.description  == new_product.description
    assert found_product.price == new_product.price
    assert found_product.category_id == new_product.category_id
    assert found_product.image_url is None

@pytest.mark.asyncio
async def test_get_by_category(product_repo,category_repo):
    tcd = CategoryCreate(   #test_category_data
            name='Laptops',
            slug="laptops"
        )
    new_category = await category_repo.create(
            category_data = tcd
        )
    test_product_data = ProductCreate(
        name = "ASUS Vivobook 14",
        description="This is laptop witgh Intel i5-13000k",
        price = 1250,
        category_id=new_category.id,
        image_url=None
    )

    new_product = await product_repo.create(
            product_data = test_product_data
        )

    found_products = await product_repo.get_by_category(
        category_id = new_category.id
    )

    assert found_products
    assert new_product.id in [product.id for product in found_products]

@pytest.mark.asyncio
async def test_create(product_repo, category_repo):
    test_category_data = CategoryCreate(
            name='Electronic',
            slug="phone"
        )
    new_category = await category_repo.create(
            category_data = test_category_data
        )
    test_product_data = ProductCreate(
        name = "IPhone 13 Max",
        description="This is iphone old",
        price = 400,
        category_id=new_category.id,
        image_url=None
    )

    new_product = await product_repo.create(
        product_data = test_product_data
    )

    assert new_product.id is not None,"База даннхы должна присвоить ID продукту"
    assert new_product.name == "IPhone 13 Max"
    assert new_product.description  =="This is iphone old"
    assert new_product.price == 400
    assert new_product.category_id == new_category.id
    assert new_product.image_url is None


@pytest.mark.asyncio
async def test_get_multiple_by_ids(product_repo,category_repo):

    test_category_data = CategoryCreate(
            name='Auto',
            slug="auto"
        )
    new_category = await category_repo.create(
            category_data = test_category_data
        )

    tpd_1 = ProductCreate(   #tpd - test_product_data
        name = "Audi A4 2005",
        description="This is old car",
        price = 2000,
        category_id=new_category.id,
        image_url=None
    )
    tpd_2 = ProductCreate(
            name = "Mazda CX-5 2024",
            description="This is a new car",
            price = 30000,
            category_id=new_category.id,
            image_url=None
        )

    cr_p1= await product_repo.create( #created_product - cr_p
        product_data = tpd_1
    )
    cr_p2= await product_repo.create( #created_product - cr_p
        product_data = tpd_2
    )

    products = await product_repo.get_multiple_by_ids(
        [cr_p1.id,
         cr_p2.id]
    )

    assert len(products) == 2
    assert cr_p1.id in [product.id for product in products]
    assert cr_p2.id in [product.id for product in products]
