from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


class WorkflowBase(BaseModel):
    """工作流基本信息"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    """創建工作流請求模型"""
    pass


class WorkflowUpdate(BaseModel):
    """更新工作流請求模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowStepBase(BaseModel):
    """工作流步驟基本信息"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    order: int = Field(..., ge=1)
    approver_role: str = Field(..., min_length=2, max_length=50)
    is_required: bool = True


class WorkflowStepCreate(WorkflowStepBase):
    """創建工作流步驟請求模型"""
    pass


class WorkflowStepUpdate(BaseModel):
    """更新工作流步驟請求模型"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    approver_role: Optional[str] = Field(None, min_length=2, max_length=50)
    is_required: Optional[bool] = None


class WorkflowStepResponse(BaseModel):
    """工作流步驟響應模型"""
    id: uuid.UUID
    workflow_id: uuid.UUID
    name: str
    description: Optional[str] = None
    order: int
    approver_role: str
    is_required: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class WorkflowResponse(BaseModel):
    """工作流響應模型"""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_active: bool
    steps: List[WorkflowStepResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class WorkflowListResponse(BaseModel):
    """工作流列表響應模型"""
    items: List[WorkflowResponse]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True