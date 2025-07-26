from pydantic import BaseModel, Field, validator, UUID4
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid


# 基礎模型
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# 文檔創建請求
class DocumentCreate(BaseSchema):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    summary: Optional[str] = None
    category_id: UUID4
    creator_id: UUID4
    is_published: bool = False
    tag_ids: Optional[List[UUID4]] = None


# 文檔更新請求
class DocumentUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    summary: Optional[str] = None
    category_id: Optional[UUID4] = None
    is_published: Optional[bool] = None


# 文檔列表響應
class DocumentListResponse(BaseSchema):
    id: UUID4
    title: str
    summary: Optional[str] = None
    category_id: UUID4
    category_name: Optional[str] = None
    creator_id: UUID4
    creator_name: Optional[str] = None
    is_published: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None


# 文檔標籤響應
class DocumentTagResponse(BaseSchema):
    id: UUID4
    name: str
    description: Optional[str] = None


# 文檔詳情響應
class DocumentResponse(DocumentListResponse):
    content: str
    attachments_count: int = 0
    comments_count: int = 0
    questions_count: int = 0
    tags: List[DocumentTagResponse] = []


# 文檔評論創建請求
class DocumentCommentCreate(BaseSchema):
    document_id: UUID4
    user_id: UUID4
    content: str = Field(..., min_length=1)


# 文檔評論響應
class DocumentCommentResponse(BaseSchema):
    id: UUID4
    document_id: UUID4
    user_id: UUID4
    user_name: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime


# 文檔附件響應
class DocumentAttachmentResponse(BaseSchema):
    id: UUID4
    document_id: UUID4
    user_id: UUID4
    user_name: Optional[str] = None
    filename: str
    file_path: str
    file_type: str
    file_size: int
    created_at: datetime