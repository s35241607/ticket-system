from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


class SearchResult(BaseModel):
    """搜索結果項"""
    id: uuid.UUID
    type: str  # document 或 question
    title: str
    content: str
    highlight: Dict[str, List[str]]  # 高亮片段，字段名 -> 高亮片段列表
    category_id: Optional[uuid.UUID] = None
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: uuid.UUID
    user_name: str
    score: float  # 相關性得分
    
    # 文檔特有字段
    is_published: Optional[bool] = None
    published_at: Optional[datetime] = None
    view_count: Optional[int] = None
    
    # 問題特有字段
    is_resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None
    answer_count: Optional[int] = None

    class Config:
        orm_mode = True


class SearchResponse(BaseModel):
    """搜索響應模型"""
    query: str
    type: str  # document, question 或 all
    results: List[SearchResult]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True