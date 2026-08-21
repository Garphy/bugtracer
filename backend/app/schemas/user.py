from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    fullname: str = Field(..., min_length=1, max_length=50)
    role: str = Field(default="coder")  # admin, coder, tester, guest

class UserCreate(UserBase):
    password: Optional[str] = Field(default="123456", min_length=4)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    fullname: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    api_key: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserSimple(BaseModel):
    id: int
    username: str
    fullname: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=4)
