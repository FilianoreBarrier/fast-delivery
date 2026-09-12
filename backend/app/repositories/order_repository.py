from app.models.order.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Order]:
        stmt = select(Order).options(selectinload(Order.order))
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, id: int) -> Order | None:
        return await self.db.get(Order, id)

    async def get_by_status(self, status: str) -> list[Order]:
        stmt = select(Order).where(Order.status == status)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_user_id(self, user_id: int) -> list[Order]:
        stmt =  select(Order).where(Order.user_id == user_id)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def create(self, order_data:OrderCreate) -> Order:
        db_order = Order(
                    user_id = order_data.user_id,
                    total_price=0.0,
                    status = "Unpaid"

                )
        self.db.add(db_order)
        await self.db.commit()
        await self.db.refresh(db_order)
        return db_order

    async def update(self, id: int, order_update:OrderUpdate) -> Order:
        order = await self.get_by_id(id)
        if order:
            update_data = order_update.model_dump(exclude_unset=True)
            for k, v in update_data.items():
                setattr(order, k, v)
            await self.db.commit()
            await self.db.refresh(order)
        return order
