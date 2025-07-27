from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

from .document import Document
from ..value_objects.approver_type import ApproverType
from ..events.document_approval_events import (
    ApprovalStepCreated, ApprovalStepUpdated, ApprovalTimeoutOccurred
)


class StepValidationError(Exception):
    """步驟驗證錯誤"""
    pass


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
        # 驗證輸入
        cls._validate_step_data(name, description, order, approver_type, 
                               approver_criteria, timeout_hours)
        
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
        
        # 發布領域事件
        step._events.append(ApprovalStepCreated(
            step_id=step_id,
            workflow_id=workflow_id,
            name=name,
            order=order,
            approver_type=approver_type.value,
            is_parallel=is_parallel,
            created_by=None  # 需要從應用層傳入
        ))
        
        return step

    def resolve_approvers(self, document: Document) -> List[uuid.UUID]:
        """解析審批者列表"""
        approvers = []
        
        if self.approver_type == ApproverType.INDIVIDUAL:
            # 個人審批者
            if 'user_ids' in self.approver_criteria:
                try:
                    approvers.extend([uuid.UUID(uid) for uid in self.approver_criteria['user_ids']])
                except (ValueError, TypeError) as e:
                    raise StepValidationError(f"無效的用戶ID格式: {e}")
        
        elif self.approver_type == ApproverType.ROLE:
            # 基於角色的審批者 - 這裡需要與用戶服務整合
            # 暫時返回空列表，實際實現時需要調用用戶服務
            # 在實際實現中，這裡會調用用戶服務來獲取具有指定角色的用戶
            if 'roles' in self.approver_criteria:
                # 這裡應該調用用戶服務API
                pass
        
        elif self.approver_type == ApproverType.DEPARTMENT:
            # 基於部門的審批者 - 這裡需要與用戶服務整合
            # 暫時返回空列表，實際實現時需要調用用戶服務
            if 'department_ids' in self.approver_criteria:
                # 這裡應該調用用戶服務API
                pass
        
        elif self.approver_type == ApproverType.CREATOR_MANAGER:
            # 創建者的主管 - 這裡需要與用戶服務整合
            # 暫時返回空列表，實際實現時需要調用用戶服務
            # 這裡應該調用用戶服務API來獲取創建者的主管
            pass
        
        return approvers

    def is_timeout_exceeded(self, approval_created_at: datetime) -> bool:
        """檢查是否超時"""
        if not self.timeout_hours:
            return False
        
        elapsed_hours = (datetime.now() - approval_created_at).total_seconds() / 3600
        return elapsed_hours > self.timeout_hours

    def get_timeout_deadline(self, approval_created_at: datetime) -> Optional[datetime]:
        """獲取超時截止時間"""
        if not self.timeout_hours:
            return None
        return approval_created_at + timedelta(hours=self.timeout_hours)

    def can_approve(self, user_id: uuid.UUID, document: Document) -> bool:
        """檢查用戶是否可以審批此步驟"""
        approvers = self.resolve_approvers(document)
        return user_id in approvers

    def update_approver_criteria(self, new_criteria: Dict[str, Any]) -> None:
        """更新審批者條件"""
        if not new_criteria:
            raise StepValidationError("審批者條件不能為空")
            
        # 驗證新條件的格式
        self._validate_approver_criteria(self.approver_type, new_criteria)
        
        old_criteria = self.approver_criteria.copy()
        self.approver_criteria = new_criteria
        
        # 發布領域事件
        self._events.append(ApprovalStepUpdated(
            step_id=self.id,
            workflow_id=self.workflow_id,
            changes={'approver_criteria': {'old': old_criteria, 'new': new_criteria}},
            updated_by=None  # 需要從應用層傳入
        ))

    def update_timeout_settings(self, timeout_hours: Optional[int], 
                               auto_approve_on_timeout: bool = False) -> None:
        """更新超時設置"""
        if timeout_hours is not None and timeout_hours <= 0:
            raise StepValidationError("超時時間必須大於0")
            
        changes = {}
        
        if self.timeout_hours != timeout_hours:
            changes['timeout_hours'] = {'old': self.timeout_hours, 'new': timeout_hours}
            self.timeout_hours = timeout_hours
            
        if self.auto_approve_on_timeout != auto_approve_on_timeout:
            changes['auto_approve_on_timeout'] = {
                'old': self.auto_approve_on_timeout, 
                'new': auto_approve_on_timeout
            }
            self.auto_approve_on_timeout = auto_approve_on_timeout
            
        if changes:
            # 發布領域事件
            self._events.append(ApprovalStepUpdated(
                step_id=self.id,
                workflow_id=self.workflow_id,
                changes=changes,
                updated_by=None  # 需要從應用層傳入
            ))

    def handle_timeout(self, approval_id: uuid.UUID) -> None:
        """處理步驟超時"""
        if not self.timeout_hours:
            return
            
        # 發布超時事件
        self._events.append(ApprovalTimeoutOccurred(
            approval_id=approval_id,
            step_id=self.id,
            timeout_hours=self.timeout_hours,
            escalation_required=not self.auto_approve_on_timeout
        ))

    def get_required_approver_count(self) -> int:
        """獲取所需審批者數量"""
        if self.approver_type == ApproverType.INDIVIDUAL:
            if 'user_ids' in self.approver_criteria:
                return len(self.approver_criteria['user_ids'])
        elif 'min_approvers' in self.approver_criteria:
            return self.approver_criteria.get('min_approvers', 1)
        return 1

    def is_sequential_step(self) -> bool:
        """檢查是否為順序步驟"""
        return not self.is_parallel

    def validate_step_configuration(self) -> List[str]:
        """驗證步驟配置，返回錯誤列表"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("步驟名稱不能為空")
            
        if not self.description or not self.description.strip():
            errors.append("步驟描述不能為空")
            
        if self.order <= 0:
            errors.append("步驟順序必須大於0")
            
        if not self.approver_criteria:
            errors.append("審批者條件不能為空")
        else:
            try:
                self._validate_approver_criteria(self.approver_type, self.approver_criteria)
            except StepValidationError as e:
                errors.append(str(e))
                
        if self.timeout_hours is not None and self.timeout_hours <= 0:
            errors.append("超時時間必須大於0")
            
        return errors

    @staticmethod
    def _validate_step_data(name: str, description: str, order: int,
                           approver_type: ApproverType, approver_criteria: Dict[str, Any],
                           timeout_hours: Optional[int] = None) -> None:
        """驗證步驟數據"""
        if not name or not name.strip():
            raise StepValidationError("步驟名稱不能為空")
            
        if not description or not description.strip():
            raise StepValidationError("步驟描述不能為空")
            
        if len(name) > 200:
            raise StepValidationError("步驟名稱不能超過200個字符")
            
        if len(description) > 1000:
            raise StepValidationError("步驟描述不能超過1000個字符")
            
        if order <= 0:
            raise StepValidationError("步驟順序必須大於0")
            
        # CREATOR_MANAGER 類型允許空條件
        if not approver_criteria and approver_type != ApproverType.CREATOR_MANAGER:
            raise StepValidationError("審批者條件不能為空")
            
        DocumentApprovalStep._validate_approver_criteria(approver_type, approver_criteria)
        
        if timeout_hours is not None and timeout_hours <= 0:
            raise StepValidationError("超時時間必須大於0")

    @staticmethod
    def _validate_approver_criteria(approver_type: ApproverType, 
                                   criteria: Dict[str, Any]) -> None:
        """驗證審批者條件"""
        if approver_type == ApproverType.INDIVIDUAL:
            if 'user_ids' not in criteria:
                raise StepValidationError("個人審批者類型必須包含 user_ids")
            if not isinstance(criteria['user_ids'], list) or not criteria['user_ids']:
                raise StepValidationError("user_ids 必須是非空列表")
                
        elif approver_type == ApproverType.ROLE:
            if 'roles' not in criteria:
                raise StepValidationError("角色審批者類型必須包含 roles")
            if not isinstance(criteria['roles'], list) or not criteria['roles']:
                raise StepValidationError("roles 必須是非空列表")
                
        elif approver_type == ApproverType.DEPARTMENT:
            if 'department_ids' not in criteria:
                raise StepValidationError("部門審批者類型必須包含 department_ids")
            if not isinstance(criteria['department_ids'], list) or not criteria['department_ids']:
                raise StepValidationError("department_ids 必須是非空列表")
                
        elif approver_type == ApproverType.CREATOR_MANAGER:
            # 創建者主管類型不需要額外條件
            pass

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events