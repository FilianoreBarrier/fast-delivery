from datetime import datetime, timezone
import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.models.user.token_blacklist import TokenBlackList
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.token_repository = TokenRepository(db)

    async def authenticate_user(self, email: str, password: str) -> UserResponse:
        """Проверка учетных данных пользователя для входа"""
        user = await self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )

        return UserResponse.model_validate(user)

    async def blacklist_token(self, token: str) -> bool:
        """Инвалидация токена (выход из системы)"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            exp_timestamp = payload.get("exp")

            if exp_timestamp is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token payload: missing exp"
                )

            expire_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            expire_time = expire_time.replace(tzinfo=None)

        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token"
            )

        db_token = TokenBlackList(token=token, expires_at=expire_time)
        await self.token_repository.add_to_blacklist(db_token)

        return True
