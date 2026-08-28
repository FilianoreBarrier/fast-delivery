from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order.order import Order
from app.core.database import Base
from sqlalchemy.orm import relationship, mapped_column, Mapped

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username:Mapped[str] = mapped_column (unique=True,index=True)
    email:Mapped[str]  = mapped_column(unique=True, index=True)
    hashed_password:Mapped[str]  = mapped_column()
    full_name:Mapped[str| None] = mapped_column ()
    is_active:Mapped[bool]  = mapped_column(default=True)
    role: Mapped[str] = mapped_column(index=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"
