from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from ..entities.document import Document
from ..entities.document_approval_workflow import DocumentApprovalWorkflow


class DocumentApprovalWorkflowRepository(ABC):
    """文檔審批工作流儲存庫介面"""

    @abstractmethod
    def save(self, workflow: DocumentApprovalWorkflow) -> DocumentApprovalWorkflow:
        """保存工作流"""
        pass

    @abstractmethod
    def get_by_id(self, workflow_id: uuid.UUID) -> Optional[DocumentApprovalWorkflow]:
        """根據ID獲取工作流"""
        pass

    @abstractmethod
    def find_applicable_workflow(self, document: Document) -> Optional[DocumentApprovalWorkflow]:
        """查找適用於指定文檔的工作流"""
        pass

    @abstractmethod
    def list_active_workflows(self) -> List[DocumentApprovalWorkflow]:
        """獲取所有活躍的工作流"""
        pass

    @abstractmethod
    def list_workflows(self, filters: Dict[str, Any] = None, 
                      skip: int = 0, limit: int = 100) -> List[DocumentApprovalWorkflow]:
        """獲取工作流列表"""
        pass

    @abstractmethod
    def delete(self, workflow_id: uuid.UUID) -> bool:
        """刪除工作流"""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[DocumentApprovalWorkflow]:
        """根據名稱獲取工作流"""
        pass