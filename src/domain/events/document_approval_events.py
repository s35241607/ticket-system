from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
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