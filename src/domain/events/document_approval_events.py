from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from .base_event import DomainEvent


@dataclass
class DocumentSubmittedForApproval(DomainEvent):
    """文檔提交審批事件"""
    document_id: uuid.UUID
    approval_id: uuid.UUID
    workflow_id: uuid.UUID
    submitted_by: uuid.UUID
    approvers: List[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DocumentApproved(DomainEvent):
    """文檔批准事件"""
    document_id: uuid.UUID
    approval_id: uuid.UUID
    approver_id: uuid.UUID
    step_id: uuid.UUID
    comment: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DocumentRejected(DomainEvent):
    """文檔拒絕事件"""
    document_id: uuid.UUID
    approval_id: uuid.UUID
    approver_id: uuid.UUID
    step_id: uuid.UUID
    comment: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DocumentChangesRequested(DomainEvent):
    """文檔要求修改事件"""
    document_id: uuid.UUID
    approval_id: uuid.UUID
    approver_id: uuid.UUID
    step_id: uuid.UUID
    comment: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalStepCompleted(DomainEvent):
    """審批步驟完成事件"""
    approval_id: uuid.UUID
    step_id: uuid.UUID
    next_step_id: Optional[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalTimeoutOccurred(DomainEvent):
    """審批超時事件"""
    approval_id: uuid.UUID
    step_id: uuid.UUID
    timeout_hours: int
    escalation_required: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalWorkflowCompleted(DomainEvent):
    """審批工作流完成事件"""
    approval_id: uuid.UUID
    document_id: uuid.UUID
    final_status: str
    completed_by: uuid.UUID
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalWorkflowCreated(DomainEvent):
    """審批工作流創建事件"""
    workflow_id: uuid.UUID
    name: str
    description: str
    created_by: Optional[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalWorkflowUpdated(DomainEvent):
    """審批工作流更新事件"""
    workflow_id: uuid.UUID
    changes: Dict[str, Any]
    updated_by: Optional[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalWorkflowActivated(DomainEvent):
    """審批工作流啟用事件"""
    workflow_id: uuid.UUID
    activated_by: Optional[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalWorkflowDeactivated(DomainEvent):
    """審批工作流停用事件"""
    workflow_id: uuid.UUID
    deactivated_by: Optional[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalStepCreated(DomainEvent):
    """審批步驟創建事件"""
    step_id: uuid.UUID
    workflow_id: uuid.UUID
    name: str
    order: int
    approver_type: str
    is_parallel: bool
    created_by: Optional[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalStepUpdated(DomainEvent):
    """審批步驟更新事件"""
    step_id: uuid.UUID
    workflow_id: uuid.UUID
    changes: Dict[str, Any]
    updated_by: Optional[uuid.UUID]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalActionCreated(DomainEvent):
    """審批行為創建事件"""
    action_id: uuid.UUID
    approval_id: uuid.UUID
    step_id: uuid.UUID
    approver_id: uuid.UUID
    action_type: str
    comment: str
    timestamp: datetime = field(default_factory=datetime.now)