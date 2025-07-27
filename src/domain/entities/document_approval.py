from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any
import uuid

from ..value_objects.approval_status import ApprovalStatus
from ..value_objects.approval_action_type import ApprovalActionType
from ..events.document_approval_events import (
    DocumentSubmittedForApproval, DocumentApproved, DocumentRejected,
    DocumentChangesRequested, ApprovalStepCompleted, ApprovalWorkflowCompleted
)


@dataclass
class DocumentApproval:
    """文檔審批實體"""
    id: uuid.UUID
    document_id: uuid.UUID
    workflow_id: uuid.UUID
    current_step_id: Optional[uuid.UUID] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    submitted_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    submitted_by: uuid.UUID = None
    _events: List[Any] = field(default_factory=list, init=False)

    @classmethod
    def create(cls, document_id: uuid.UUID, workflow_id: uuid.UUID,
               submitted_by: uuid.UUID) -> 'DocumentApproval':
        """創建新的文檔審批"""
        approval_id = uuid.uuid4()
        approval = cls(
            id=approval_id,
            document_id=document_id,
            workflow_id=workflow_id,
            submitted_by=submitted_by,
            status=ApprovalStatus.PENDING
        )
        return approval

    def submit_for_approval(self, workflow: 'DocumentApprovalWorkflow',
                          approvers: List[uuid.UUID]) -> None:
        """提交審批"""
        if self.status != ApprovalStatus.PENDING:
            raise ValueError("只能提交待審批狀態的文檔")

        first_step = workflow.get_first_step()
        if not first_step:
            raise ValueError("工作流沒有定義審批步驟")

        self.current_step_id = first_step.id
        self.status = ApprovalStatus.IN_PROGRESS
        
        # 發布領域事件
        self._events.append(DocumentSubmittedForApproval(
            document_id=self.document_id,
            approval_id=self.id,
            workflow_id=self.workflow_id,
            submitted_by=self.submitted_by,
            approvers=approvers
        ))

    def approve_step(self, step_id: uuid.UUID, approver_id: uuid.UUID, 
                    comment: str) -> None:
        """批准當前步驟"""
        if self.status != ApprovalStatus.IN_PROGRESS:
            raise ValueError("只能批准進行中的審批")
        
        if self.current_step_id != step_id:
            raise ValueError("只能批准當前步驟")

        # 發布領域事件
        self._events.append(DocumentApproved(
            document_id=self.document_id,
            approval_id=self.id,
            approver_id=approver_id,
            step_id=step_id,
            comment=comment
        ))

    def reject(self, step_id: uuid.UUID, approver_id: uuid.UUID, 
              comment: str) -> None:
        """拒絕審批"""
        if self.status != ApprovalStatus.IN_PROGRESS:
            raise ValueError("只能拒絕進行中的審批")
        
        if self.current_step_id != step_id:
            raise ValueError("只能拒絕當前步驟")

        self.status = ApprovalStatus.REJECTED
        self.completed_at = datetime.now()

        # 發布領域事件
        self._events.append(DocumentRejected(
            document_id=self.document_id,
            approval_id=self.id,
            approver_id=approver_id,
            step_id=step_id,
            comment=comment
        ))

        self._events.append(ApprovalWorkflowCompleted(
            approval_id=self.id,
            document_id=self.document_id,
            final_status=self.status.value,
            completed_by=approver_id
        ))

    def request_changes(self, step_id: uuid.UUID, approver_id: uuid.UUID,
                       comment: str) -> None:
        """要求修改"""
        if self.status != ApprovalStatus.IN_PROGRESS:
            raise ValueError("只能對進行中的審批要求修改")
        
        if self.current_step_id != step_id:
            raise ValueError("只能對當前步驟要求修改")

        self.status = ApprovalStatus.REQUIRES_CHANGES
        self.completed_at = datetime.now()

        # 發布領域事件
        self._events.append(DocumentChangesRequested(
            document_id=self.document_id,
            approval_id=self.id,
            approver_id=approver_id,
            step_id=step_id,
            comment=comment
        ))

    def progress_to_next_step(self, next_step_id: Optional[uuid.UUID]) -> None:
        """進入下一個審批步驟"""
        if self.status != ApprovalStatus.IN_PROGRESS:
            raise ValueError("只能推進進行中的審批")

        current_step_id = self.current_step_id
        
        if next_step_id:
            self.current_step_id = next_step_id
        else:
            # 沒有下一步，完成審批
            self.complete_approval()

        # 發布領域事件
        self._events.append(ApprovalStepCompleted(
            approval_id=self.id,
            step_id=current_step_id,
            next_step_id=next_step_id
        ))

    def complete_approval(self) -> None:
        """完成審批"""
        if self.status != ApprovalStatus.IN_PROGRESS:
            raise ValueError("只能完成進行中的審批")

        self.status = ApprovalStatus.APPROVED
        self.completed_at = datetime.now()
        self.current_step_id = None

        # 發布領域事件
        self._events.append(ApprovalWorkflowCompleted(
            approval_id=self.id,
            document_id=self.document_id,
            final_status=self.status.value,
            completed_by=self.submitted_by  # 或者最後一個審批者
        ))

    def cancel(self) -> None:
        """取消審批"""
        if self.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
            raise ValueError("無法取消已完成的審批")

        self.status = ApprovalStatus.CANCELLED
        self.completed_at = datetime.now()
        self.current_step_id = None

    def reset_for_resubmission(self, new_workflow_id: Optional[uuid.UUID] = None) -> None:
        """重置審批以便重新提交"""
        if self.status != ApprovalStatus.REQUIRES_CHANGES:
            raise ValueError("只能重置需要修改的審批")

        self.status = ApprovalStatus.PENDING
        self.current_step_id = None
        self.completed_at = None
        
        if new_workflow_id:
            self.workflow_id = new_workflow_id

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events