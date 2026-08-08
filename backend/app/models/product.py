from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship, mapped_column, Mapped
if TYPE_CHECKING:
    from .category import Category
from sqlalchemy import (Text, ForeignKey, DateTime)
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str|None] = mapped_column(Text)
    price: Mapped[float] = mapped_column()
    image_url:Mapped[str|None] = mapped_column()
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id",ondelete ="CASCADE"))

    category: Mapped[Category] = relationship(back_populates='products')

    def __repr__(self):
        return f'<Product(id={self.id},name = "{self.name}",price ={self.price})>'
