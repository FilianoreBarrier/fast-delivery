from typing import Optional
from pydantic import BaseModel,ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20, description="Unique username")
    email: EmailStr= Field(description="User email for authorization")
    full_name: Optional[str] = Field(default=None,max_length=50,description='User full name')

class UserCreate(UserBase):
    password: str = Field(min_length=8, description='User password for authorization')

class UserResponse(UserBase):
    user_id: int = Field(description="Unique user identifier")
    is_active: bool = Field(description='Shows user activity ')
    role: str = Field(description=":buyer or seller")
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserInternalUpdate(UserUpdate):
    is_active: Optional[bool] = None
    hashed_password: Optional[str] = None

class UserPublicResponse(BaseModel):
    user_id: int= Field(description="Unique user identifier")
    username: str
    full_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class LoginSchema(BaseModel):
    email: EmailStr = Field(description="Email for login")
    password: str = Field(description="Password for login")

class ChangePasswordSchema(BaseModel):
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)
