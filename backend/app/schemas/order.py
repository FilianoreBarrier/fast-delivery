from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class OrderBase(BaseModel):
    user_id: int

class OrderItemResponse(BaseModel):
    order_id: int
    product_id: int
    price: float
    quantity: int
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(OrderBase):

    id: int = Field(description='Unique order ID')
    created_at: datetime
    status: str = Field(description='Unpaid/Processing/In Delivery/Delivered')
    total_price: float
    order_items: list[OrderItemResponse]
    model_config = ConfigDict(from_attributes=True)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = Field(description="Default - unpaid")
