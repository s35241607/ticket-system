from pydantic import BaseModel, Field, validator, UUID4
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid


# 基礎模型
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# 問題創建請求
class QuestionCreate(BaseSchema):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    document_id: UUID4
    user_id: UUID4


# 問題更新請求
class QuestionUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    is_resolved: Optional[bool] = None


# 問題列表響應
class QuestionListResponse(BaseSchema):
    id: UUID4
    title: str
    document_id: UUID4
    document_title: Optional[str] = None
    user_id: UUID4
    user_name: Optional[str] = None
    is_resolved: bool
    view_count: int
    answers_count: int = 0
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


# 問題詳情響應
class QuestionResponse(QuestionListResponse):
    content: str
    accepted_answer_id: Optional[UUID4] = None


# 回答創建請求
class AnswerCreate(BaseSchema):
    question_id: UUID4
    user_id: UUID4
    content: str = Field(..., min_length=1)


# 回答更新請求
class AnswerUpdate(BaseSchema):
    content: Optional[str] = Field(None, min_length=1)


# 回答響應
class AnswerResponse(BaseSchema):
    id: UUID4
    question_id: UUID4
    user_id: UUID4
    user_name: Optional[str] = None
    content: str
    is_accepted: bool
    upvotes_count: int = 0
    downvotes_count: int = 0
    created_at: datetime
    updated_at: datetime
    accepted_at: Optional[datetime] = None


# 回答投票創建請求
class AnswerVoteCreate(BaseSchema):
    answer_id: UUID4
    user_id: UUID4
    is_upvote: bool