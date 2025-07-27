from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any, Dict
import uuid

from ..value_objects.approval_status import ApprovalStatus
from ..value_objects.approval_action_type import ApprovalActionType
from ..events.document_approval_events import (
    DocumentSubmittedForApproval, DocumentApproved, DocumentRejected,
    DocumentChangesRequested, ApprovalStepCompleted, ApprovalWorkflowCompleted
)


class ApprovalStateError(Exception):
    """審批狀態錯誤"""
    pass


class ApprovalValidationError(Exception):
    """審批驗證錯誤"""
    pass


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
        if not document_id or not workflow_id or not submitted_by:
            raise ApprovalValidationError("文檔ID、工作流ID和提交者ID不能為空")
            
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
        # 驗證狀態轉換
        if not self._can_transition_to(ApprovalStatus.IN_PROGRESS):
            raise ApprovalStateError(f"無法從 {self.status.value} 狀態提交審批")

        if not workflow:
            raise ApprovalValidationError("工作流不能為空")

        first_step = workflow.get_first_step()
        if not first_step:
            raise ApprovalValidationError("工作流沒有定義審批步驟")

        if not approvers:
            raise ApprovalValidationError("審批者列表不能為空")

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
        # 驗證狀態
        if not self._can_perform_action():
            raise ApprovalStateError(f"無法在 {self.status.value} 狀態下執行批准操作")
        
        # 驗證步驟
        if not self._is_current_step(step_id):
            raise ApprovalValidationError("只能批准當前步驟")

        # 驗證輸入
        if not approver_id:
            raise ApprovalValidationError("審批者ID不能為空")
            
        if not comment or not comment.strip():
            raise ApprovalValidationError("審批意見不能為空")

        # 發布領域事件
        self._events.append(DocumentApproved(
            document_id=self.document_id,
            approval_id=self.id,
            approver_id=approver_id,
            step_id=step_id,
            comment=comment.strip()
        ))

    def reject(self, step_id: uuid.UUID, approver_id: uuid.UUID, 
              comment: str) -> None:
        """拒絕審批"""
        # 驗證狀態
        if not self._can_perform_action():
            raise ApprovalStateError(f"無法在 {self.status.value} 狀態下執行拒絕操作")
        
        # 驗證步驟
        if not self._is_current_step(step_id):
            raise ApprovalValidationError("只能拒絕當前步驟")

        # 驗證輸入
        if not approver_id:
            raise ApprovalValidationError("審批者ID不能為空")
            
        if not comment or not comment.strip():
            raise ApprovalValidationError("拒絕理由不能為空")

        # 驗證狀態轉換
        if not self._can_transition_to(ApprovalStatus.REJECTED):
            raise ApprovalStateError(f"無法從 {self.status.value} 狀態轉換到 REJECTED")

        self.status = ApprovalStatus.REJECTED
        self.completed_at = datetime.now()
        self.current_step_id = None

        # 發布領域事件
        self._events.append(DocumentRejected(
            document_id=self.document_id,
            approval_id=self.id,
            approver_id=approver_id,
            step_id=step_id,
            comment=comment.strip()
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
        # 驗證狀態
        if not self._can_perform_action():
            raise ApprovalStateError(f"無法在 {self.status.value} 狀態下執行要求修改操作")
        
        # 驗證步驟
        if not self._is_current_step(step_id):
            raise ApprovalValidationError("只能對當前步驟要求修改")

        # 驗證輸入
        if not approver_id:
            raise ApprovalValidationError("審批者ID不能為空")
            
        if not comment or not comment.strip():
            raise ApprovalValidationError("修改要求不能為空")

        # 驗證狀態轉換
        if not self._can_transition_to(ApprovalStatus.REQUIRES_CHANGES):
            raise ApprovalStateError(f"無法從 {self.status.value} 狀態轉換到 REQUIRES_CHANGES")

        self.status = ApprovalStatus.REQUIRES_CHANGES
        self.completed_at = datetime.now()
        self.current_step_id = None

        # 發布領域事件
        self._events.append(DocumentChangesRequested(
            document_id=self.document_id,
            approval_id=self.id,
            approver_id=approver_id,
            step_id=step_id,
            comment=comment.strip()
        ))

    def progress_to_next_step(self, next_step_id: Optional[uuid.UUID]) -> None:
        """進入下一個審批步驟"""
        # 驗證狀態
        if not self._can_perform_action():
            raise ApprovalStateError(f"無法在 {self.status.value} 狀態下推進步驟")

        current_step_id = self.current_step_id
        
        if next_step_id:
            # 進入下一步
            if next_step_id == current_step_id:
                raise ApprovalValidationError("下一步驟不能與當前步驟相同")
            self.current_step_id = next_step_id
        else:
            # 沒有下一步，完成審批
            self.complete_approval()
            return

        # 發布領域事件
        self._events.append(ApprovalStepCompleted(
            approval_id=self.id,
            step_id=current_step_id,
            next_step_id=next_step_id
        ))

    def complete_approval(self, completed_by: Optional[uuid.UUID] = None) -> None:
        """完成審批"""
        # 驗證狀態轉換
        if not self._can_transition_to(ApprovalStatus.APPROVED):
            raise ApprovalStateError(f"無法從 {self.status.value} 狀態完成審批")

        self.status = ApprovalStatus.APPROVED
        self.completed_at = datetime.now()
        self.current_step_id = None

        # 發布領域事件
        self._events.append(ApprovalWorkflowCompleted(
            approval_id=self.id,
            document_id=self.document_id,
            final_status=self.status.value,
            completed_by=completed_by or self.submitted_by
        ))

    def cancel(self, cancelled_by: uuid.UUID, reason: str = "") -> None:
        """取消審批"""
        # 驗證狀態轉換
        if not self._can_transition_to(ApprovalStatus.CANCELLED):
            raise ApprovalStateError(f"無法從 {self.status.value} 狀態取消審批")

        if not cancelled_by:
            raise ApprovalValidationError("取消者ID不能為空")

        self.status = ApprovalStatus.CANCELLED
        self.completed_at = datetime.now()
        self.current_step_id = None

        # 發布領域事件
        self._events.append(ApprovalWorkflowCompleted(
            approval_id=self.id,
            document_id=self.document_id,
            final_status=self.status.value,
            completed_by=cancelled_by
        ))

    def reset_for_resubmission(self, new_workflow_id: Optional[uuid.UUID] = None) -> None:
        """重置審批以便重新提交"""
        # 驗證狀態轉換
        if not self._can_transition_to(ApprovalStatus.PENDING):
            raise ApprovalStateError(f"無法從 {self.status.value} 狀態重置審批")

        self.status = ApprovalStatus.PENDING
        self.current_step_id = None
        self.completed_at = None
        
        if new_workflow_id:
            self.workflow_id = new_workflow_id

    def is_in_progress(self) -> bool:
        """檢查是否正在進行中"""
        return self.status == ApprovalStatus.IN_PROGRESS

    def is_completed(self) -> bool:
        """檢查是否已完成（批准、拒絕或取消）"""
        return self.status in [
            ApprovalStatus.APPROVED, 
            ApprovalStatus.REJECTED, 
            ApprovalStatus.CANCELLED
        ]

    def is_pending_changes(self) -> bool:
        """檢查是否需要修改"""
        return self.status == ApprovalStatus.REQUIRES_CHANGES

    def get_duration(self) -> Optional[int]:
        """獲取審批持續時間（秒）"""
        if not self.completed_at:
            return None
        return int((self.completed_at - self.submitted_at).total_seconds())

    def get_current_step_duration(self) -> Optional[int]:
        """獲取當前步驟持續時間（秒）"""
        if not self.current_step_id:
            return None
        # 這裡需要從步驟開始時間計算，暫時使用提交時間
        return int((datetime.now() - self.submitted_at).total_seconds())

    def validate_approval_state(self) -> List[str]:
        """驗證審批狀態，返回錯誤列表"""
        errors = []
        
        if not self.document_id:
            errors.append("文檔ID不能為空")
            
        if not self.workflow_id:
            errors.append("工作流ID不能為空")
            
        if not self.submitted_by:
            errors.append("提交者ID不能為空")
            
        if self.status == ApprovalStatus.IN_PROGRESS and not self.current_step_id:
            errors.append("進行中的審批必須有當前步驟")
            
        if self.is_completed() and not self.completed_at:
            errors.append("已完成的審批必須有完成時間")
            
        if self.completed_at and self.completed_at < self.submitted_at:
            errors.append("完成時間不能早於提交時間")
            
        return errors

    def _can_transition_to(self, target_status: ApprovalStatus) -> bool:
        """檢查是否可以轉換到目標狀態"""
        valid_transitions = {
            ApprovalStatus.PENDING: [ApprovalStatus.IN_PROGRESS, ApprovalStatus.CANCELLED],
            ApprovalStatus.IN_PROGRESS: [
                ApprovalStatus.APPROVED, 
                ApprovalStatus.REJECTED, 
                ApprovalStatus.REQUIRES_CHANGES,
                ApprovalStatus.CANCELLED
            ],
            ApprovalStatus.REQUIRES_CHANGES: [ApprovalStatus.PENDING, ApprovalStatus.CANCELLED],
            ApprovalStatus.APPROVED: [],  # 終態
            ApprovalStatus.REJECTED: [],  # 終態
            ApprovalStatus.CANCELLED: []  # 終態
        }
        
        return target_status in valid_transitions.get(self.status, [])

    def _can_perform_action(self) -> bool:
        """檢查是否可以執行審批操作"""
        return self.status == ApprovalStatus.IN_PROGRESS

    def _is_current_step(self, step_id: uuid.UUID) -> bool:
        """檢查是否為當前步驟"""
        return self.current_step_id == step_id

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events