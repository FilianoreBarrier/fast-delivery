from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user.user import User
from app.services.cart_service import CartService
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from pydantic import BaseModel

router = APIRouter(prefix="/cart", tags=["cart"])

class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int

class UpdateCartRequest(BaseModel):
    product_id: int
    quantity: int


@router.post("/add", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def add_to_cart(
    request: AddToCartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db)
    item = CartItemCreate(product_id=request.product_id, quantity=request.quantity)
    return await service.add_to_cart(current_user.id, item)


@router.get("/", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db)
    return await service.get_cart(current_user.id)


@router.put("/update", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def update_cart_item(
    request: UpdateCartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db)
    item = CartItemUpdate(product_id=request.product_id, quantity=request.quantity)
    return await service.update_cart_item(current_user.id,item)


@router.delete("/remove/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def remove_from_cart(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db)
    return await service.remove_from_cart(current_user.id,product_id)
