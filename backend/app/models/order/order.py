from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .order_item import OrderItem
    from app.models.user.user import User
from datetime import datetime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy import ForeignKey


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),index=True)
    status: Mapped[str] = mapped_column(index=True,default='Unpaid')
    total_price: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    order_items:Mapped[list["OrderItem"]] = relationship(back_populates='order')
    user:Mapped["User"]  = relationship(back_populates='orders')
    def __repr__(self):
        return f"<Order {self.status}>"
