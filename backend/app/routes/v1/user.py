from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse, UserUpdate,UserPublicResponse, ChangePasswordSchema
from app.services.user_service import UserService
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user.user import User

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get('/{user_id}', response_model=UserPublicResponse, status_code= status.HTTP_200_OK)
async def get_user(user_id:int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    user_service = UserService(db)
    return await user_service.get_by_id(user_id)
