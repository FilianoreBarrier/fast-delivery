from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.services.order_service import OrderService
from app.schemas.user import UserResponse
from app.schemas.order import OrderResponse,OrderCreate
from app.schemas.cart import CartResponse
from app.core.security import get_current_user
from app.models.user.user import User

router = APIRouter(prefix='/orders', tags=['/orders'] )

@router.get("/",response_model=List[OrderResponse], status_code=status.HTTP_200_OK)
async def get_orders(db:AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)
                     ):
    order_service = OrderService(db)
    return await order_service.get_orders(current_user.id)

@router.post('/', response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание заказа из текущей корзины пользователя"""
    order_service = OrderService(db)
    return await order_service.create_order_from_cart(current_user.id)
