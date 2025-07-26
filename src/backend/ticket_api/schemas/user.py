from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
import uuid
from datetime import datetime


class UserBase(BaseModel):
    """用戶基本信息"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    department_id: Optional[uuid.UUID] = None
    is_active: bool = True
    role: str = Field(..., min_length=2, max_length=50)


class UserCreate(UserBase):
    """創建用戶請求模型"""
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        """驗證密碼強度"""
        if len(v) < 8:
            raise ValueError('密碼長度必須至少為8個字符')
        if not any(char.isdigit() for char in v):
            raise ValueError('密碼必須包含至少一個數字')
        if not any(char.isupper() for char in v):
            raise ValueError('密碼必須包含至少一個大寫字母')
        if not any(char.islower() for char in v):
            raise ValueError('密碼必須包含至少一個小寫字母')
        return v


class UserUpdate(BaseModel):
    """更新用戶請求模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    department_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None
    role: Optional[str] = Field(None, min_length=2, max_length=50)
    password: Optional[str] = Field(None, min_length=8)

    @validator('password')
    def password_strength(cls, v):
        """驗證密碼強度"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('密碼長度必須至少為8個字符')
        if not any(char.isdigit() for char in v):
            raise ValueError('密碼必須包含至少一個數字')
        if not any(char.isupper() for char in v):
            raise ValueError('密碼必須包含至少一個大寫字母')
        if not any(char.islower() for char in v):
            raise ValueError('密碼必須包含至少一個小寫字母')
        return v


class DepartmentResponse(BaseModel):
    """部門響應模型"""
    id: uuid.UUID
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """用戶響應模型"""
    id: uuid.UUID
    username: str
    email: EmailStr
    full_name: str
    department_id: Optional[uuid.UUID] = None
    department: Optional[DepartmentResponse] = None
    is_active: bool
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    """用戶列表響應模型"""
    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True