from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship, mapped_column, Mapped
if TYPE_CHECKING:
    from .product import Product
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str] = mapped_column(unique=True,index=True)
    slug:Mapped[str] = mapped_column(unique=True,index=True)

    products:Mapped[list[Product]] = relationship(back_populates='category')

    def __repr__(self):
        return f'<Category(id={self.id}, name = "{self.name}")>'
