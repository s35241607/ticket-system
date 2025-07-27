from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Optional, Dict
import uuid

from ..value_objects.approval_action_type import ApprovalActionType
from ..events.document_approval_events import ApprovalActionCreated


class ActionValidationError(Exception):
    """行為驗證錯誤"""
    pass


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
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    _events: List[Any] = field(default_factory=list, init=False)

    @classmethod
    def create_approval_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                              approver_id: uuid.UUID, action_type: ApprovalActionType,
                              comment: str, metadata: Optional[Dict[str, Any]] = None) -> 'DocumentApprovalAction':
        """創建審批行為記錄"""
        # 驗證輸入
        cls._validate_action_data(approval_id, step_id, approver_id, action_type, comment)
        
        action_id = uuid.uuid4()
        action = cls(
            id=action_id,
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=action_type,
            comment=comment.strip(),
            metadata=metadata or {}
        )
        
        # 發布領域事件
        action._events.append(ApprovalActionCreated(
            action_id=action_id,
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=action_type.value,
            comment=comment.strip()
        ))
        
        return action

    @classmethod
    def create_approve_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                             approver_id: uuid.UUID, comment: str,
                             metadata: Optional[Dict[str, Any]] = None) -> 'DocumentApprovalAction':
        """創建批准行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.APPROVE,
            comment=comment,
            metadata=metadata
        )

    @classmethod
    def create_reject_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                            approver_id: uuid.UUID, comment: str,
                            metadata: Optional[Dict[str, Any]] = None) -> 'DocumentApprovalAction':
        """創建拒絕行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.REJECT,
            comment=comment,
            metadata=metadata
        )

    @classmethod
    def create_request_changes_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                                     approver_id: uuid.UUID, comment: str,
                                     metadata: Optional[Dict[str, Any]] = None) -> 'DocumentApprovalAction':
        """創建要求修改行為記錄"""
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.REQUEST_CHANGES,
            comment=comment,
            metadata=metadata
        )

    @classmethod
    def create_escalate_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                              approver_id: uuid.UUID, comment: str,
                              escalated_to: Optional[uuid.UUID] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> 'DocumentApprovalAction':
        """創建升級行為記錄"""
        escalate_metadata = metadata or {}
        if escalated_to:
            escalate_metadata['escalated_to'] = str(escalated_to)
            
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=ApprovalActionType.ESCALATE,
            comment=comment,
            metadata=escalate_metadata
        )

    @classmethod
    def create_auto_approve_action(cls, approval_id: uuid.UUID, step_id: uuid.UUID,
                                  system_user_id: uuid.UUID, comment: str,
                                  timeout_hours: Optional[int] = None,
                                  metadata: Optional[Dict[str, Any]] = None) -> 'DocumentApprovalAction':
        """創建自動批准行為記錄"""
        auto_approve_metadata = metadata or {}
        auto_approve_metadata['is_system_action'] = True
        if timeout_hours:
            auto_approve_metadata['timeout_hours'] = timeout_hours
            
        return cls.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=system_user_id,
            action_type=ApprovalActionType.AUTO_APPROVE,
            comment=comment,
            metadata=auto_approve_metadata
        )

    def is_system_action(self) -> bool:
        """檢查是否為系統行為"""
        return self.metadata.get('is_system_action', False)

    def is_escalation_action(self) -> bool:
        """檢查是否為升級行為"""
        return self.action_type == ApprovalActionType.ESCALATE

    def is_timeout_action(self) -> bool:
        """檢查是否為超時相關行為"""
        return (self.action_type == ApprovalActionType.AUTO_APPROVE and 
                'timeout_hours' in self.metadata)

    def get_escalated_to(self) -> Optional[uuid.UUID]:
        """獲取升級目標審批者"""
        if not self.is_escalation_action():
            return None
        escalated_to_str = self.metadata.get('escalated_to')
        if escalated_to_str:
            try:
                return uuid.UUID(escalated_to_str)
            except ValueError:
                return None
        return None

    def get_timeout_hours(self) -> Optional[int]:
        """獲取超時小時數"""
        return self.metadata.get('timeout_hours')

    def add_metadata(self, key: str, value: Any) -> None:
        """添加元數據"""
        if not key or not key.strip():
            raise ActionValidationError("元數據鍵不能為空")
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """獲取元數據"""
        return self.metadata.get(key, default)

    def get_action_summary(self) -> str:
        """獲取行為摘要"""
        action_names = {
            ApprovalActionType.APPROVE: "批准",
            ApprovalActionType.REJECT: "拒絕",
            ApprovalActionType.REQUEST_CHANGES: "要求修改",
            ApprovalActionType.ESCALATE: "升級",
            ApprovalActionType.AUTO_APPROVE: "自動批准"
        }
        
        action_name = action_names.get(self.action_type, "未知行為")
        
        # 優先檢查超時行為，因為超時行為也是系統行為
        if self.is_timeout_action():
            timeout_hours = self.get_timeout_hours()
            return f"超時{action_name}（{timeout_hours}小時）"
        elif self.is_escalation_action():
            escalated_to = self.get_escalated_to()
            if escalated_to:
                return f"{action_name}至 {escalated_to}"
            return action_name
        elif self.is_system_action():
            return f"系統{action_name}"
        else:
            return action_name

    def validate_action(self) -> List[str]:
        """驗證行為記錄，返回錯誤列表"""
        errors = []
        
        if not self.approval_id:
            errors.append("審批ID不能為空")
            
        if not self.step_id:
            errors.append("步驟ID不能為空")
            
        if not self.approver_id:
            errors.append("審批者ID不能為空")
            
        if not self.comment or not self.comment.strip():
            errors.append("評論不能為空")
            
        if len(self.comment) > 2000:
            errors.append("評論不能超過2000個字符")
            
        # 驗證升級行為的元數據
        if self.is_escalation_action():
            escalated_to = self.get_escalated_to()
            if not escalated_to:
                errors.append("升級行為必須指定升級目標")
                
        # 驗證自動批准行為的元數據
        if self.action_type == ApprovalActionType.AUTO_APPROVE:
            if not self.is_system_action():
                errors.append("自動批准行為必須標記為系統行為")
                
        return errors

    @staticmethod
    def _validate_action_data(approval_id: uuid.UUID, step_id: uuid.UUID,
                             approver_id: uuid.UUID, action_type: ApprovalActionType,
                             comment: str) -> None:
        """驗證行為數據"""
        if not approval_id:
            raise ActionValidationError("審批ID不能為空")
            
        if not step_id:
            raise ActionValidationError("步驟ID不能為空")
            
        if not approver_id:
            raise ActionValidationError("審批者ID不能為空")
            
        if not action_type:
            raise ActionValidationError("行為類型不能為空")
            
        if not comment or not comment.strip():
            raise ActionValidationError("評論不能為空")
            
        if len(comment) > 2000:
            raise ActionValidationError("評論不能超過2000個字符")

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events