from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any
import uuid

from ..value_objects.approval_action_type import ApprovalActionType


@dataclass
class DocumentApprovalAction:
    """文檔審批行為實體"""
    id: uuid.UUID
    approval_id: uuid.UUID
    step_id: uuid.UUID
    approver_id: uuid.UUID
    action_type: ApprovalActionType
    comment: str
    created_at: datetime = field(default_factory=datetime.now)
    _events: List[Any] = field(default_factory=list, init=False)

    @classmethod
    def create_approval_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                              approver_id: uuid.UUID, action_type: ApprovalActionType,
                              comment: str) -> 'DocumentApprovalAction':
        """創建審批行為記錄"""
        action_id = uuid.uuid4()
        action = cls(
            id=action_id,
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=action_type,
            comment=comment
        )
        return action

    @classmethod
    def create_approve_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                             approver_id: uuid.UUID, comment: str) -> 'DocumentApprovalAction':
        """創建批准行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.APPROVE,
            comment=comment
        )

    @classmethod
    def create_reject_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                            approver_id: uuid.UUID, comment: str) -> 'DocumentApprovalAction':
        """創建拒絕行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.REJECT,
            comment=comment
        )

    @classmethod
    def create_request_changes_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                                     approver_id: uuid.UUID, comment: str) -> 'DocumentApprovalAction':
        """創建要求修改行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.REQUEST_CHANGES,
            comment=comment
        )

    @classmethod
    def create_escalate_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                              approver_id: uuid.UUID, comment: str) -> 'DocumentApprovalAction':
        """創建升級行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.ESCALATE,
            comment=comment
        )

    @classmethod
    def create_auto_approve_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                                  system_user_id: uuid.UUID, comment: str) -> 'DocumentApprovalAction':
        """創建自動批准行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=system_user_id,
            action_type=ApprovalActionType.AUTO_APPROVE,
            comment=comment
        )

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events