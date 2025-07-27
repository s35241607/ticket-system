from typing import Optional
import uuid

from ...domain.entities.document_approval import DocumentApproval
from ...domain.repositories.document_repository import DocumentRepository
from ...domain.repositories.document_approval_repository import DocumentApprovalRepository
from ...domain.repositories.document_approval_workflow_repository import DocumentApprovalWorkflowRepository
from ...domain.events.event_publisher import EventPublisher


class SubmitDocumentForApprovalUseCase:
    """提交文檔審批用例"""

    def __init__(
        self,
        document_repo: DocumentRepository,
        approval_repo: DocumentApprovalRepository,
        workflow_repo: DocumentApprovalWorkflowRepository,
        event_publisher: EventPublisher
    ):
        self.document_repo = document_repo
        self.approval_repo = approval_repo
        self.workflow_repo = workflow_repo
        self.event_publisher = event_publisher

    def execute(
        self, 
        document_id: uuid.UUID, 
        submitted_by: uuid.UUID,
        workflow_id: Optional[uuid.UUID] = None
    ) -> DocumentApproval:
        """執行提交文檔審批用例"""
        # TODO: 實現用例邏輯
        # 1. 驗證文檔存在且可以提交審批
        # 2. 選擇或驗證工作流
        # 3. 創建審批記錄
        # 4. 解析審批者
        # 5. 提交審批
        # 6. 保存審批記錄
        # 7. 發布領域事件
        raise NotImplementedError("功能尚未實現")