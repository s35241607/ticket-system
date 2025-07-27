from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from ..entities.document_approval_action import DocumentApprovalAction
from ..value_objects.approval_action_type import ApprovalActionType


class DocumentApprovalActionRepository(ABC):
    """文檔審批行為儲存庫介面"""

    @abstractmethod
    def save(self, action: DocumentApprovalAction) -> DocumentApprovalAction:
        """保存審批行為記錄"""
        pass

    @abstractmethod
    def get_by_id(self, action_id: uuid.UUID) -> Optional[DocumentApprovalAction]:
        """根據ID獲取審批行為記錄"""
        pass

    @abstractmethod
    def find_by_approval_id(self, approval_id: uuid.UUID) -> List[DocumentApprovalAction]:
        """根據審批ID查找所有行為記錄"""
        pass

    @abstractmethod
    def find_by_approver_id(self, approver_id: uuid.UUID,
                           skip: int = 0, limit: int = 100) -> List[DocumentApprovalAction]:
        """根據審批者ID查找行為記錄"""
        pass

    @abstractmethod
    def find_by_action_type(self, action_type: ApprovalActionType,
                           skip: int = 0, limit: int = 100) -> List[DocumentApprovalAction]:
        """根據行為類型查找記錄"""
        pass

    @abstractmethod
    def find_by_step_id(self, step_id: uuid.UUID) -> List[DocumentApprovalAction]:
        """根據步驟ID查找行為記錄"""
        pass

    @abstractmethod
    def find_by_date_range(self, start_date, end_date,
                          skip: int = 0, limit: int = 100) -> List[DocumentApprovalAction]:
        """根據日期範圍查找行為記錄"""
        pass

    @abstractmethod
    def list_actions(self, filters: Dict[str, Any] = None,
                    skip: int = 0, limit: int = 100) -> List[DocumentApprovalAction]:
        """獲取審批行為記錄列表"""
        pass

    @abstractmethod
    def delete(self, action_id: uuid.UUID) -> bool:
        """刪除審批行為記錄"""
        pass