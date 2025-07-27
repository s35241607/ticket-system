from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from ..entities.document_approval import DocumentApproval
from ..value_objects.approval_status import ApprovalStatus


class DocumentApprovalRepository(ABC):
    """文檔審批儲存庫介面"""

    @abstractmethod
    def save(self, approval: DocumentApproval) -> DocumentApproval:
        """保存審批記錄"""
        pass

    @abstractmethod
    def get_by_id(self, approval_id: uuid.UUID) -> Optional[DocumentApproval]:
        """根據ID獲取審批記錄"""
        pass

    @abstractmethod
    def get_by_document_id(self, document_id: uuid.UUID) -> Optional[DocumentApproval]:
        """根據文檔ID獲取審批記錄"""
        pass

    @abstractmethod
    def find_pending_approvals_for_user(self, user_id: uuid.UUID) -> List[DocumentApproval]:
        """查找用戶待審批的文檔"""
        pass

    @abstractmethod
    def find_approvals_by_status(self, status: ApprovalStatus, 
                                skip: int = 0, limit: int = 100) -> List[DocumentApproval]:
        """根據狀態查找審批記錄"""
        pass

    @abstractmethod
    def find_approvals_by_submitter(self, submitter_id: uuid.UUID,
                                   skip: int = 0, limit: int = 100) -> List[DocumentApproval]:
        """根據提交者查找審批記錄"""
        pass

    @abstractmethod
    def find_approvals_by_workflow(self, workflow_id: uuid.UUID,
                                  skip: int = 0, limit: int = 100) -> List[DocumentApproval]:
        """根據工作流查找審批記錄"""
        pass

    @abstractmethod
    def find_timeout_approvals(self, timeout_hours: int) -> List[DocumentApproval]:
        """查找超時的審批記錄"""
        pass

    @abstractmethod
    def list_approvals(self, filters: Dict[str, Any] = None,
                      skip: int = 0, limit: int = 100) -> List[DocumentApproval]:
        """獲取審批記錄列表"""
        pass

    @abstractmethod
    def delete(self, approval_id: uuid.UUID) -> bool:
        """刪除審批記錄"""
        pass