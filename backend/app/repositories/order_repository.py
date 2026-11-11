from app.models.order.order import Order
from app.models.order.order_item import OrderItem
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderStatus
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Order]:
        stmt = select(Order).options(selectinload(Order.order_items))
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, id: int) -> Order | None:
        return await self.db.get(Order, id)

    async def get_by_status(self, status: str) -> list[Order]:
        stmt = select(Order).where(Order.status == status)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_user_id(self, user_id: int) -> list[Order]:
        stmt =  select(Order).where(Order.user_id == user_id).options(selectinload(Order.order_items)) #загружаем товары сразу
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, order_data: OrderCreate, total_price: float) -> Order:
        db_order = Order(
            user_id=order_data.user_id,
            total_price=total_price,
            status=OrderStatus.UNPAID
        )
        self.db.add(db_order)
        await self.db.flush()  # Генерируем ID, но не закрываем транзакцию
        return db_order

    async def status_update(self, id: int, order_update:OrderStatusUpdate) -> Order:
        order = await self.get_by_id(id)
        if order:
            update_data = order_update.model_dump(exclude_unset=True)
            for k, v in update_data.items():
                setattr(order, k, v)
            await self.db.commit()
            await self.db.refresh(order)
        return order

    async def create_items(self, items:list[OrderItem])-> None:
        self.db.add_all(items)
        await self.db.commit()

    async def get_order_with_items(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.order_items))
            .execution_options(populate_existing=True)  # <-- Принудительно берем свежие данные из БД
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
