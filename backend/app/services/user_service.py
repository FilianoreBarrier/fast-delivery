from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import raise_user_not_found
from app.core.security import get_password_hash, verify_password
from app.repositories.user_repository import UserRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserInternalUpdate

class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.order_repository = OrderRepository(db)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        if await self.user_repository.get_by_email(user_data.email):
            raise HTTPException(
                 status_code=status.HTTP_409_CONFLICT,
                 detail='The email is already taken.'
             )  # ошибка "email уже занят"
        if await self.user_repository.get_by_username(user_data.username):
            raise HTTPException(
                 status_code=status.HTTP_409_CONFLICT,
                 detail='The username is already taken'
             )  # ошибка "username уже занят"
        hashed_password = get_password_hash(user_data.password)
        user = await self.user_repository.create(user_data, hashed_password, "buyer")
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise_user_not_found(user_id)
        updated_user = await self.user_repository.update(user_id,user_update)
        return UserResponse.model_validate(updated_user)

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> UserResponse:
        """Смена пароля пользователя"""

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise_user_not_found(user_id)

        if not verify_password(old_password, user.hashed_password):# type: ignore[attr-async defined]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect old password"
            )

        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )

        new_hashed_password = get_password_hash(new_password)
        updated_user = await self.user_repository.update(user_id, UserInternalUpdate(hashed_password= new_hashed_password))

        return UserResponse.model_validate(updated_user)

    async def list_users(self) -> List[UserResponse]:
        users = await self.user_repository.get_all()
        return [UserResponse.model_validate(user) for user in users]

    '''get methods'''
    async def get_by_id(self, user_id: int) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise_user_not_found(user_id)
        return UserResponse.model_validate(user)

    async def get_by_email(self, email: str) -> UserResponse:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found."
            )
        return UserResponse.model_validate(user)

    async def get_by_username(self, username: str) -> UserResponse:
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this username not found."
            )
        return UserResponse.model_validate(user)

    async def get_batch_users_by_ids(self, ids: List[int]) -> List[UserResponse]:
        if not ids:
            return []
        users = await self.user_repository.get_multiple_by_ids(ids)
        return [UserResponse.model_validate(user) for user in users]
