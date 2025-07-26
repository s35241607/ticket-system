from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


class CategoryBase(BaseModel):
    """分類基本信息"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class CategoryCreate(CategoryBase):
    """創建分類請求模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新分類請求模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class CategoryResponse(BaseModel):
    """分類響應模型"""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    children: List['CategoryResponse'] = []

    class Config:
        orm_mode = True


# 解決循環引用問題
CategoryResponse.update_forward_refs()


class CategoryListResponse(BaseModel):
    """分類列表響應模型"""
    items: List[CategoryResponse]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True