import uuid

from ...domain.entities.document_approval import DocumentApproval
from ...domain.repositories.document_approval_repository import DocumentApprovalRepository
from ...domain.repositories.document_approval_workflow_repository import DocumentApprovalWorkflowRepository
from ...domain.repositories.document_approval_action_repository import DocumentApprovalActionRepository
from ...domain.events.event_publisher import EventPublisher
from ...domain.value_objects.approval_action_type import ApprovalActionType


class ProcessApprovalDecisionUseCase:
    """處理審批決定用例"""

    def __init__(
        self,
        approval_repo: DocumentApprovalRepository,
        workflow_repo: DocumentApprovalWorkflowRepository,
        action_repo: DocumentApprovalActionRepository,
        event_publisher: EventPublisher
    ):
        self.approval_repo = approval_repo
        self.workflow_repo = workflow_repo
        self.action_repo = action_repo
        self.event_publisher = event_publisher

    def execute(
        self,
        approval_id: uuid.UUID,
        approver_id: uuid.UUID,
        action: ApprovalActionType,
        comment: str
    ) -> DocumentApproval:
        """執行處理審批決定用例"""
        # TODO: 實現用例邏輯
        # 1. 獲取審批記錄
        # 2. 獲取工作流和當前步驟
        # 3. 驗證審批者權限
        # 4. 執行審批行為
        # 5. 記錄審批行為
        # 6. 更新審批狀態
        # 7. 保存審批記錄
        # 8. 發布領域事件
        raise NotImplementedError("功能尚未實現")