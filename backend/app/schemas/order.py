from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.order.order import OrderStatus

class OrderBase(BaseModel):
    user_id: int

class OrderItemResponse(BaseModel):
    order_id: int
    product_id: int
    price: float
    quantity: int
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status:OrderStatus

class OrderResponse(OrderBase):

    id: int = Field(description='Unique order ID')
    created_at: datetime
    status: OrderStatus = Field(description='Current status of the order')
    total_price: float
    order_items: list[OrderItemResponse]
    model_config = ConfigDict(from_attributes=True)

class OrderCreate(OrderBase):
    pass
