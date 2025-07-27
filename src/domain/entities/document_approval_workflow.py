from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from .document import Document
from ..events.document_approval_events import (
    ApprovalWorkflowCreated, ApprovalWorkflowUpdated, 
    ApprovalWorkflowActivated, ApprovalWorkflowDeactivated
)


class WorkflowValidationError(Exception):
    """工作流驗證錯誤"""
    pass


@dataclass
class DocumentApprovalWorkflow:
    """文檔審批工作流實體"""
    id: uuid.UUID
    name: str
    description: str
    category_criteria: Optional[Dict[str, Any]] = None
    tag_criteria: Optional[Dict[str, Any]] = None
    creator_criteria: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    steps: List['DocumentApprovalStep'] = field(default_factory=list)
    _events: List[Any] = field(default_factory=list, init=False)

    @classmethod
    def create(cls, name: str, description: str, 
               category_criteria: Optional[Dict[str, Any]] = None,
               tag_criteria: Optional[Dict[str, Any]] = None,
               creator_criteria: Optional[Dict[str, Any]] = None) -> 'DocumentApprovalWorkflow':
        """創建新的審批工作流"""
        # 驗證輸入
        cls._validate_workflow_data(name, description, category_criteria, tag_criteria, creator_criteria)
        
        workflow_id = uuid.uuid4()
        workflow = cls(
            id=workflow_id,
            name=name,
            description=description,
            category_criteria=category_criteria,
            tag_criteria=tag_criteria,
            creator_criteria=creator_criteria
        )
        
        # 發布領域事件
        workflow._events.append(ApprovalWorkflowCreated(
            workflow_id=workflow_id,
            name=name,
            description=description,
            created_by=None  # 需要從應用層傳入
        ))
        
        return workflow

    def add_step(self, step: 'DocumentApprovalStep') -> None:
        """添加審批步驟"""
        if not self.is_active:
            raise WorkflowValidationError("無法向非活動工作流添加步驟")
            
        # 檢查步驟是否已存在
        if any(s.id == step.id for s in self.steps):
            raise WorkflowValidationError("步驟已存在於工作流中")
            
        # 檢查順序是否衝突
        if any(s.order == step.order for s in self.steps):
            raise WorkflowValidationError(f"步驟順序 {step.order} 已被使用")
            
        # 驗證步驟屬於此工作流
        if step.workflow_id != self.id:
            raise WorkflowValidationError("步驟不屬於此工作流")
            
        self.steps.append(step)
        self.steps.sort(key=lambda s: s.order)
        self.updated_at = datetime.now()
        
        # 發布領域事件
        self._events.append(ApprovalWorkflowUpdated(
            workflow_id=self.id,
            changes={'steps': f'添加步驟: {step.name}'},
            updated_by=None  # 需要從應用層傳入
        ))

    def remove_step(self, step_id: uuid.UUID) -> None:
        """移除審批步驟"""
        if not self.is_active:
            raise WorkflowValidationError("無法從非活動工作流移除步驟")
            
        step_to_remove = next((s for s in self.steps if s.id == step_id), None)
        if not step_to_remove:
            raise WorkflowValidationError("步驟不存在於工作流中")
            
        self.steps = [step for step in self.steps if step.id != step_id]
        self.updated_at = datetime.now()
        
        # 發布領域事件
        self._events.append(ApprovalWorkflowUpdated(
            workflow_id=self.id,
            changes={'steps': f'移除步驟: {step_to_remove.name}'},
            updated_by=None  # 需要從應用層傳入
        ))

    def get_applicable_documents(self, document: Document) -> bool:
        """檢查工作流是否適用於指定文檔"""
        if not self.is_active:
            return False
            
        if not self.steps:
            return False  # 沒有步驟的工作流不適用

        # 檢查分類條件
        if self.category_criteria:
            if not self._matches_criteria(document.category_id, self.category_criteria):
                return False

        # 檢查標籤條件
        if self.tag_criteria:
            if not self._matches_tag_criteria(document.tags, self.tag_criteria):
                return False

        # 檢查創建者條件
        if self.creator_criteria:
            if not self._matches_criteria(document.creator_id, self.creator_criteria):
                return False

        return True

    def get_first_step(self) -> Optional['DocumentApprovalStep']:
        """獲取第一個審批步驟"""
        if not self.steps:
            return None
        return min(self.steps, key=lambda s: s.order)

    def get_next_step(self, current_step_id: uuid.UUID) -> Optional['DocumentApprovalStep']:
        """獲取下一個審批步驟"""
        current_step = next((s for s in self.steps if s.id == current_step_id), None)
        if not current_step:
            return None

        next_steps = [s for s in self.steps if s.order > current_step.order]
        if not next_steps:
            return None

        return min(next_steps, key=lambda s: s.order)

    def activate(self) -> None:
        """啟用工作流"""
        if self.is_active:
            return  # 已經是活動狀態
            
        if not self.steps:
            raise WorkflowValidationError("無法啟用沒有步驟的工作流")
            
        # 驗證步驟順序的連續性
        self._validate_step_sequence()
        
        self.is_active = True
        self.updated_at = datetime.now()
        
        # 發布領域事件
        self._events.append(ApprovalWorkflowActivated(
            workflow_id=self.id,
            activated_by=None  # 需要從應用層傳入
        ))

    def deactivate(self) -> None:
        """停用工作流"""
        if not self.is_active:
            return  # 已經是非活動狀態
            
        self.is_active = False
        self.updated_at = datetime.now()
        
        # 發布領域事件
        self._events.append(ApprovalWorkflowDeactivated(
            workflow_id=self.id,
            deactivated_by=None  # 需要從應用層傳入
        ))

    def _matches_criteria(self, value: Any, criteria: Dict[str, Any]) -> bool:
        """檢查值是否符合條件"""
        # 簡單的條件匹配邏輯，可以根據需要擴展
        if 'equals' in criteria:
            return str(value) == str(criteria['equals'])
        if 'in' in criteria:
            return str(value) in [str(v) for v in criteria['in']]
        return True

    def _matches_tag_criteria(self, tags: List[uuid.UUID], criteria: Dict[str, Any]) -> bool:
        """檢查標籤是否符合條件"""
        if 'contains_any' in criteria:
            required_tags = [uuid.UUID(tag) for tag in criteria['contains_any']]
            return any(tag in tags for tag in required_tags)
        if 'contains_all' in criteria:
            required_tags = [uuid.UUID(tag) for tag in criteria['contains_all']]
            return all(tag in tags for tag in required_tags)
        return True

    def update_criteria(self, category_criteria: Optional[Dict[str, Any]] = None,
                       tag_criteria: Optional[Dict[str, Any]] = None,
                       creator_criteria: Optional[Dict[str, Any]] = None) -> None:
        """更新工作流條件"""
        changes = {}
        
        if category_criteria is not None:
            changes['category_criteria'] = {'old': self.category_criteria, 'new': category_criteria}
            self.category_criteria = category_criteria
            
        if tag_criteria is not None:
            changes['tag_criteria'] = {'old': self.tag_criteria, 'new': tag_criteria}
            self.tag_criteria = tag_criteria
            
        if creator_criteria is not None:
            changes['creator_criteria'] = {'old': self.creator_criteria, 'new': creator_criteria}
            self.creator_criteria = creator_criteria
            
        if changes:
            self.updated_at = datetime.now()
            
            # 發布領域事件
            self._events.append(ApprovalWorkflowUpdated(
                workflow_id=self.id,
                changes=changes,
                updated_by=None  # 需要從應用層傳入
            ))

    def get_step_by_order(self, order: int) -> Optional['DocumentApprovalStep']:
        """根據順序獲取步驟"""
        return next((step for step in self.steps if step.order == order), None)

    def get_parallel_steps(self, order: int) -> List['DocumentApprovalStep']:
        """獲取指定順序的所有並行步驟"""
        return [step for step in self.steps if step.order == order and step.is_parallel]

    def has_parallel_steps(self) -> bool:
        """檢查工作流是否包含並行步驟"""
        return any(step.is_parallel for step in self.steps)

    def validate_workflow(self) -> List[str]:
        """驗證工作流完整性，返回錯誤列表"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("工作流名稱不能為空")
            
        if not self.description or not self.description.strip():
            errors.append("工作流描述不能為空")
            
        if not self.steps:
            errors.append("工作流必須至少包含一個步驟")
        else:
            # 檢查步驟順序
            orders = [step.order for step in self.steps]
            if len(orders) != len(set(orders)):
                errors.append("步驟順序不能重複")
                
            # 檢查順序連續性
            sorted_orders = sorted(orders)
            for i, order in enumerate(sorted_orders):
                if i == 0 and order != 1:
                    errors.append("步驟順序必須從1開始")
                elif i > 0 and order != sorted_orders[i-1] + 1:
                    errors.append(f"步驟順序不連續：缺少順序 {sorted_orders[i-1] + 1}")
                    
        return errors

    @staticmethod
    def _validate_workflow_data(name: str, description: str,
                               category_criteria: Optional[Dict[str, Any]] = None,
                               tag_criteria: Optional[Dict[str, Any]] = None,
                               creator_criteria: Optional[Dict[str, Any]] = None) -> None:
        """驗證工作流數據"""
        if not name or not name.strip():
            raise WorkflowValidationError("工作流名稱不能為空")
            
        if not description or not description.strip():
            raise WorkflowValidationError("工作流描述不能為空")
            
        if len(name) > 200:
            raise WorkflowValidationError("工作流名稱不能超過200個字符")
            
        if len(description) > 1000:
            raise WorkflowValidationError("工作流描述不能超過1000個字符")

    def _validate_step_sequence(self) -> None:
        """驗證步驟順序的連續性"""
        if not self.steps:
            return
            
        orders = sorted([step.order for step in self.steps])
        
        # 檢查是否從1開始
        if orders[0] != 1:
            raise WorkflowValidationError("步驟順序必須從1開始")
            
        # 檢查連續性
        for i in range(1, len(orders)):
            if orders[i] != orders[i-1] + 1:
                raise WorkflowValidationError(f"步驟順序不連續：缺少順序 {orders[i-1] + 1}")

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events