from pydantic import Field, BaseModel, ConfigDict
from typing import Optional

class CartItemBase(BaseModel):
    product_id: int = Field(description='Product ID')
    quantity: int = Field(gt = 0, description='Quantity (must be greater than 0)')

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    product_id: int = Field(description='Product ID')
    quantity: int = Field(gt=0, description="New quantity (must be greater than 0)")

class CartItem(CartItemBase):
    name: str = Field(description="Product name")
    price: float = Field(description='Product price')
    subtotal: float = Field(description='Total price for this item (price * quantity)')
    image_url: Optional[str] = Field(None,description='Product image URL')
    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    items: list[CartItem] = Field( description='List of items in cart.')
    total: float=Field(description='Total cart price')
    items_count: int = Field(description='Total number of items in cart')
    model_config = ConfigDict(from_attributes=True)
