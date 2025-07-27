from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ....domain.value_objects.approval_status import ApprovalStatus
from ....domain.value_objects.approval_action_type import ApprovalActionType
from ....domain.value_objects.approver_type import ApproverType


class SubmitApprovalRequest(BaseModel):
    """提交審批請求"""
    workflow_id: Optional[uuid.UUID] = Field(None, description="指定工作流ID，如果不指定則自動選擇")
    comment: Optional[str] = Field(None, description="提交說明")

    class Config:
        schema_extra = {
            "example": {
                "workflow_id": "123e4567-e89b-12d3-a456-426614174000",
                "comment": "請審批此文檔"
            }
        }


class ApprovalDecisionRequest(BaseModel):
    """審批決定請求"""
    comment: str = Field(..., description="審批意見", min_length=1, max_length=1000)

    class Config:
        schema_extra = {
            "example": {
                "comment": "文檔內容符合要求，批准發布"
            }
        }


class BatchApprovalRequest(BaseModel):
    """批量審批請求"""
    approval_ids: List[uuid.UUID] = Field(..., description="審批ID列表", min_items=1)
    comment: str = Field(..., description="批量審批意見", min_length=1, max_length=1000)

    class Config:
        schema_extra = {
            "example": {
                "approval_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ],
                "comment": "批量批准這些文檔"
            }
        }


class DocumentApprovalStepResponse(BaseModel):
    """審批步驟回應"""
    id: uuid.UUID
    name: str
    description: str
    order: int
    approver_type: ApproverType
    is_parallel: bool
    timeout_hours: Optional[int]
    auto_approve_on_timeout: bool

    class Config:
        use_enum_values = True


class DocumentApprovalWorkflowResponse(BaseModel):
    """審批工作流回應"""
    id: uuid.UUID
    name: str
    description: str
    is_active: bool
    steps: List[DocumentApprovalStepResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        use_enum_values = True


class DocumentApprovalResponse(BaseModel):
    """文檔審批回應"""
    id: uuid.UUID
    document_id: uuid.UUID
    workflow_id: uuid.UUID
    current_step_id: Optional[uuid.UUID]
    status: ApprovalStatus
    submitted_at: datetime
    completed_at: Optional[datetime]
    submitted_by: uuid.UUID
    workflow: Optional[DocumentApprovalWorkflowResponse] = None

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "document_id": "123e4567-e89b-12d3-a456-426614174001",
                "workflow_id": "123e4567-e89b-12d3-a456-426614174002",
                "current_step_id": "123e4567-e89b-12d3-a456-426614174003",
                "status": "in_progress",
                "submitted_at": "2024-01-01T00:00:00Z",
                "completed_at": None,
                "submitted_by": "123e4567-e89b-12d3-a456-426614174004"
            }
        }


class ApprovalHistoryResponse(BaseModel):
    """審批歷史回應"""
    id: uuid.UUID
    approval_id: uuid.UUID
    step_id: uuid.UUID
    approver_id: uuid.UUID
    action_type: ApprovalActionType
    comment: str
    created_at: datetime

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "approval_id": "123e4567-e89b-12d3-a456-426614174001",
                "step_id": "123e4567-e89b-12d3-a456-426614174002",
                "approver_id": "123e4567-e89b-12d3-a456-426614174003",
                "action_type": "approve",
                "comment": "文檔內容符合要求",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class WorkflowConfigRequest(BaseModel):
    """工作流配置請求"""
    name: str = Field(..., description="工作流名稱", min_length=1, max_length=200)
    description: str = Field(..., description="工作流描述", max_length=1000)
    category_criteria: Optional[Dict[str, Any]] = Field(None, description="分類條件")
    tag_criteria: Optional[Dict[str, Any]] = Field(None, description="標籤條件")
    creator_criteria: Optional[Dict[str, Any]] = Field(None, description="創建者條件")

    class Config:
        schema_extra = {
            "example": {
                "name": "標準文檔審批流程",
                "description": "適用於一般文檔的標準審批流程",
                "category_criteria": {"in": ["technical", "policy"]},
                "tag_criteria": {"contains_any": ["important", "public"]},
                "creator_criteria": None
            }
        }


class WorkflowStepConfigRequest(BaseModel):
    """工作流步驟配置請求"""
    name: str = Field(..., description="步驟名稱", min_length=1, max_length=200)
    description: str = Field(..., description="步驟描述", max_length=1000)
    order: int = Field(..., description="步驟順序", ge=1)
    approver_type: ApproverType = Field(..., description="審批者類型")
    approver_criteria: Dict[str, Any] = Field(..., description="審批者條件")
    is_parallel: bool = Field(False, description="是否並行審批")
    timeout_hours: Optional[int] = Field(None, description="超時小時數", ge=1)
    auto_approve_on_timeout: bool = Field(False, description="超時後是否自動批准")

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "部門主管審批",
                "description": "由部門主管進行審批",
                "order": 1,
                "approver_type": "role",
                "approver_criteria": {"roles": ["department_manager"]},
                "is_parallel": False,
                "timeout_hours": 72,
                "auto_approve_on_timeout": False
            }
        }