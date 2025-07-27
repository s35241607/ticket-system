from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from .document import Document


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
        workflow_id = uuid.uuid4()
        workflow = cls(
            id=workflow_id,
            name=name,
            description=description,
            category_criteria=category_criteria,
            tag_criteria=tag_criteria,
            creator_criteria=creator_criteria
        )
        return workflow

    def add_step(self, step: 'DocumentApprovalStep') -> None:
        """添加審批步驟"""
        if step not in self.steps:
            self.steps.append(step)
            self.steps.sort(key=lambda s: s.order)
            self.updated_at = datetime.now()

    def remove_step(self, step_id: uuid.UUID) -> None:
        """移除審批步驟"""
        self.steps = [step for step in self.steps if step.id != step_id]
        self.updated_at = datetime.now()

    def get_applicable_documents(self, document: Document) -> bool:
        """檢查工作流是否適用於指定文檔"""
        if not self.is_active:
            return False

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
        self.is_active = True
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """停用工作流"""
        self.is_active = False
        self.updated_at = datetime.now()

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

    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events