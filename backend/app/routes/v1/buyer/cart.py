from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import get_current_user
from app.models.user.user import User
from app.services.cart_service import CartService
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse

router = APIRouter(prefix="/cart", tags=["cart"])

@router.post("/add", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def add_to_cart(
    item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db, redis)
    return await service.add_to_cart(current_user.id, item)


@router.get("/", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db, redis)
    return await service.get_cart(current_user.id)


@router.put("/update", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def update_cart_item(
    item: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db, redis)
    return await service.update_cart_item(current_user.id,item)


@router.delete("/remove/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def remove_from_cart(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    service = CartService(db,redis)
    return await service.remove_from_cart(current_user.id,product_id)
