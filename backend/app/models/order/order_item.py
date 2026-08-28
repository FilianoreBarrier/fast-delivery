from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order.order import Order
from app.models.product.product import Product
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.core.database import Base
from sqlalchemy import ForeignKey


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    order_id:Mapped[int]= mapped_column(ForeignKey("orders.id",ondelete="CASCADE"),index=True)
    product_id:Mapped[int]= mapped_column(ForeignKey("products.id"),index=True)
    quantity: Mapped[int] = mapped_column()
    price:Mapped[float] = mapped_column()
    product: Mapped["Product"] = relationship()
    order:Mapped["Order"] = relationship(back_populates='order_items')


    def __repr__(self):
        return f"<OrderItem {self.id}>"
