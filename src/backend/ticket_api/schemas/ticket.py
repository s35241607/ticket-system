from pydantic import BaseModel, Field, validator, UUID4
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid


# 基礎模型
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# 工單創建請求
class TicketCreate(BaseSchema):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    creator_id: UUID4
    assignee_id: Optional[UUID4] = None
    ticket_type_id: UUID4
    ticket_status_id: UUID4
    ticket_priority_id: UUID4
    due_date: Optional[datetime] = None


# 工單更新請求
class TicketUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    assignee_id: Optional[UUID4] = None
    ticket_status_id: Optional[UUID4] = None
    ticket_priority_id: Optional[UUID4] = None
    current_workflow_step_id: Optional[UUID4] = None
    due_date: Optional[datetime] = None


# 工單列表響應
class TicketListResponse(BaseSchema):
    id: UUID4
    title: str
    creator_id: UUID4
    creator_name: Optional[str] = None
    assignee_id: Optional[UUID4] = None
    assignee_name: Optional[str] = None
    ticket_type_id: UUID4
    ticket_type_name: Optional[str] = None
    ticket_status_id: UUID4
    ticket_status_name: Optional[str] = None
    ticket_priority_id: UUID4
    ticket_priority_name: Optional[str] = None
    current_workflow_step_id: Optional[UUID4] = None
    current_workflow_step_name: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None


# 工單詳情響應
class TicketResponse(TicketListResponse):
    description: str
    department_id: Optional[UUID4] = None
    department_name: Optional[str] = None
    workflow_id: Optional[UUID4] = None
    workflow_name: Optional[str] = None
    attachments_count: int = 0
    comments_count: int = 0


# 工單評論創建請求
class TicketCommentCreate(BaseSchema):
    ticket_id: UUID4
    user_id: UUID4
    content: str = Field(..., min_length=1)


# 工單評論響應
class TicketCommentResponse(BaseSchema):
    id: UUID4
    ticket_id: UUID4
    user_id: UUID4
    user_name: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime


# 工單附件響應
class TicketAttachmentResponse(BaseSchema):
    id: UUID4
    ticket_id: UUID4
    user_id: UUID4
    user_name: Optional[str] = None
    filename: str
    file_path: str
    file_type: str
    file_size: int
    created_at: datetime


# 工作流審批創建請求
class WorkflowApprovalCreate(BaseSchema):
    ticket_id: UUID4
    workflow_step_id: UUID4
    approver_id: UUID4
    is_approved: bool
    comment: Optional[str] = None


# 工作流審批響應
class WorkflowApprovalResponse(BaseSchema):
    id: UUID4
    ticket_id: UUID4
    workflow_step_id: UUID4
    workflow_step_name: Optional[str] = None
    approver_id: UUID4
    approver_name: Optional[str] = None
    is_approved: bool
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime