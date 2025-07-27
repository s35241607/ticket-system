from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from .document import Document
from ..value_objects.approver_type import ApproverType


@dataclass
class DocumentApprovalStep:
    """文檔審批步驟實體"""
    id: uuid.UUID
    workflow_id: uuid.UUID
    name: str
    description: str
    order: int
    approver_type: ApproverType
    approver_criteria: Dict[str, Any]
    is_parallel: bool = False
    timeout_hours: Optional[int] = None
    auto_approve_on_timeout: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    _events: List[Any] = field(default_factory=list, init=False)

    @classmethod
    def create(cls, workflow_id: uuid.UUID, name: str, description: str,
               order: int, approver_type: ApproverType, 
               approver_criteria: Dict[str, Any],
               is_parallel: bool = False,
               timeout_hours: Optional[int] = None,
               auto_approve_on_timeout: bool = False) -> 'DocumentApprovalStep':
        """創建新的審批步驟"""
        step_id = uuid.uuid4()
        step = cls(
            id=step_id,
            workflow_id=workflow_id,
            name=name,
            description=description,
            order=order,
            approver_type=approver_type,
            approver_criteria=approver_criteria,
            is_parallel=is_parallel,
            timeout_hours=timeout_hours,
            auto_approve_on_timeout=auto_approve_on_timeout
        )
        return step

    def resolve_approvers(self, document: Document) -> List[uuid.UUID]:
        """解析審批者列表"""
        approvers = []
        
        if self.approver_type == ApproverType.INDIVIDUAL:
            # 個人審批者
            if 'user_ids' in self.approver_criteria:
                approvers.extend([uuid.UUID(uid) for uid in self.approver_criteria['user_ids']])
        
        elif self.approver_type == ApproverType.ROLE:
            # 基於角色的審批者 - 這裡需要與用戶服務整合
            # 暫時返回空列表，實際實現時需要調用用戶服務
            pass
        
        elif self.approver_type == ApproverType.DEPARTMENT:
            # 基於部門的審批者 - 這裡需要與用戶服務整合
            # 暫時返回空列表，實際實現時需要調用用戶服務
            pass
        
        elif self.approver_type == ApproverType.CREATOR_MANAGER:
            # 創建者的主管 - 這裡需要與用戶服務整合
            # 暫時返回空列表，實際實現時需要調用用戶服務
            pass
        
        return approvers

    def is_timeout_exceeded(self, approval_created_at: datetime) -> bool:
        """檢查是否超時"""
        if not self.timeout_hours:
            return False
        
        elapsed_hours = (datetime.now() - approval_created_at).total_seconds() / 3600
        return elapsed_hours > self.timeout_hours

    def can_approve(self, user_id: uuid.UUID, document: Document) -> bool:
        """檢查用戶是否可以審批此步驟"""
        approvers = self.resolve_approvers(document)
        return user_id in approvers

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events