from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


class DepartmentBase(BaseModel):
    """部門基本信息"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    """創建部門請求模型"""
    pass


class DepartmentUpdate(BaseModel):
    """更新部門請求模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    """部門響應模型"""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class DepartmentListResponse(BaseModel):
    """部門列表響應模型"""
    items: List[DepartmentResponse]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True