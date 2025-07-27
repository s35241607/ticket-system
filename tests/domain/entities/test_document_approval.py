import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.domain.entities.document_approval import DocumentApproval, ApprovalStateError, ApprovalValidationError
from src.domain.entities.document_approval_workflow import DocumentApprovalWorkflow
from src.domain.entities.document_approval_step import DocumentApprovalStep
from src.domain.value_objects.approval_status import ApprovalStatus
from src.domain.value_objects.approver_type import ApproverType
from src.domain.events.document_approval_events import (
    DocumentSubmittedForApproval, DocumentApproved, DocumentRejected,
    DocumentChangesRequested, ApprovalStepCompleted, ApprovalWorkflowCompleted
)


class TestDocumentApproval:
    """文檔審批實體測試"""

    def test_create_approval(self):
        """測試創建文檔審批"""
        # Arrange
        document_id = uuid.uuid4()
        workflow_id = uuid.uuid4()
        submitted_by = uuid.uuid4()

        # Act
        approval = DocumentApproval.create(
            document_id=document_id,
            workflow_id=workflow_id,
            submitted_by=submitted_by
        )

        # Assert
        assert approval.document_id == document_id
        assert approval.workflow_id == workflow_id
        assert approval.submitted_by == submitted_by
        assert approval.status == ApprovalStatus.PENDING
        assert approval.current_step_id is None
        assert approval.completed_at is None
        assert isinstance(approval.id, uuid.UUID)
        assert isinstance(approval.submitted_at, datetime)

    def test_create_approval_with_invalid_data(self):
        """測試使用無效數據創建審批"""
        # 測試空文檔ID
        with pytest.raises(ApprovalValidationError, match="文檔ID、工作流ID和提交者ID不能為空"):
            DocumentApproval.create(None, uuid.uuid4(), uuid.uuid4())

        # 測試空工作流ID
        with pytest.raises(ApprovalValidationError, match="文檔ID、工作流ID和提交者ID不能為空"):
            DocumentApproval.create(uuid.uuid4(), None, uuid.uuid4())

        # 測試空提交者ID
        with pytest.raises(ApprovalValidationError, match="文檔ID、工作流ID和提交者ID不能為空"):
            DocumentApproval.create(uuid.uuid4(), uuid.uuid4(), None)

    def test_submit_for_approval(self):
        """測試提交審批"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        workflow.add_step(step)

        approvers = [uuid.uuid4(), uuid.uuid4()]

        # Act
        approval.submit_for_approval(workflow, approvers)

        # Assert
        assert approval.status == ApprovalStatus.IN_PROGRESS
        assert approval.current_step_id == step.id

        # 檢查事件
        events = approval.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentSubmittedForApproval)
        assert events[0].approval_id == approval.id
        assert events[0].approvers == approvers

    def test_submit_for_approval_validation(self):
        """測試提交審批的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試無效狀態
        approval.status = ApprovalStatus.APPROVED
        with pytest.raises(ApprovalStateError, match="無法從 approved 狀態提交審批"):
            approval.submit_for_approval(None, [])

        # 重置狀態
        approval.status = ApprovalStatus.PENDING

        # 測試空工作流
        with pytest.raises(ApprovalValidationError, match="工作流不能為空"):
            approval.submit_for_approval(None, [])

        # 測試沒有步驟的工作流
        empty_workflow = DocumentApprovalWorkflow.create("空工作流", "描述")
        with pytest.raises(ApprovalValidationError, match="工作流沒有定義審批步驟"):
            approval.submit_for_approval(empty_workflow, [])

        # 測試空審批者列表
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        workflow.add_step(step)

        with pytest.raises(ApprovalValidationError, match="審批者列表不能為空"):
            approval.submit_for_approval(workflow, [])

    def test_approve_step(self):
        """測試批准步驟"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        step_id = uuid.uuid4()
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = step_id

        approver_id = uuid.uuid4()
        comment = "批准此文檔"

        # Act
        approval.approve_step(step_id, approver_id, comment)

        # Assert
        events = approval.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentApproved)
        assert events[0].approval_id == approval.id
        assert events[0].approver_id == approver_id
        assert events[0].step_id == step_id
        assert events[0].comment == comment

    def test_approve_step_validation(self):
        """測試批准步驟的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()

        # 測試無效狀態
        approval.status = ApprovalStatus.PENDING
        with pytest.raises(ApprovalStateError, match="無法在 pending 狀態下執行批准操作"):
            approval.approve_step(step_id, approver_id, "comment")

        # 設置正確狀態
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = uuid.uuid4()  # 不同的步驟ID

        # 測試錯誤步驟
        with pytest.raises(ApprovalValidationError, match="只能批准當前步驟"):
            approval.approve_step(step_id, approver_id, "comment")

        # 設置正確步驟
        approval.current_step_id = step_id

        # 測試空審批者ID
        with pytest.raises(ApprovalValidationError, match="審批者ID不能為空"):
            approval.approve_step(step_id, None, "comment")

        # 測試空意見
        with pytest.raises(ApprovalValidationError, match="審批意見不能為空"):
            approval.approve_step(step_id, approver_id, "")

        with pytest.raises(ApprovalValidationError, match="審批意見不能為空"):
            approval.approve_step(step_id, approver_id, "   ")

    def test_reject(self):
        """測試拒絕審批"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        step_id = uuid.uuid4()
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = step_id

        approver_id = uuid.uuid4()
        comment = "拒絕此文檔"

        # Act
        approval.reject(step_id, approver_id, comment)

        # Assert
        assert approval.status == ApprovalStatus.REJECTED
        assert approval.completed_at is not None
        assert approval.current_step_id is None

        events = approval.get_events()
        assert len(events) == 2
        assert isinstance(events[0], DocumentRejected)
        assert isinstance(events[1], ApprovalWorkflowCompleted)
        assert events[0].comment == comment
        assert events[1].final_status == ApprovalStatus.REJECTED.value

    def test_reject_validation(self):
        """測試拒絕審批的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()

        # 測試無效狀態
        approval.status = ApprovalStatus.PENDING
        with pytest.raises(ApprovalStateError, match="無法在 pending 狀態下執行拒絕操作"):
            approval.reject(step_id, approver_id, "comment")

        # 設置正確狀態
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = uuid.uuid4()  # 不同的步驟ID

        # 測試錯誤步驟
        with pytest.raises(ApprovalValidationError, match="只能拒絕當前步驟"):
            approval.reject(step_id, approver_id, "comment")

        # 設置正確步驟
        approval.current_step_id = step_id

        # 測試空審批者ID
        with pytest.raises(ApprovalValidationError, match="審批者ID不能為空"):
            approval.reject(step_id, None, "comment")

        # 測試空拒絕理由
        with pytest.raises(ApprovalValidationError, match="拒絕理由不能為空"):
            approval.reject(step_id, approver_id, "")

    def test_request_changes(self):
        """測試要求修改"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        step_id = uuid.uuid4()
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = step_id

        approver_id = uuid.uuid4()
        comment = "需要修改內容"

        # Act
        approval.request_changes(step_id, approver_id, comment)

        # Assert
        assert approval.status == ApprovalStatus.REQUIRES_CHANGES
        assert approval.completed_at is not None
        assert approval.current_step_id is None

        events = approval.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentChangesRequested)
        assert events[0].comment == comment

    def test_request_changes_validation(self):
        """測試要求修改的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()

        # 測試無效狀態
        approval.status = ApprovalStatus.PENDING
        with pytest.raises(ApprovalStateError, match="無法在 pending 狀態下執行要求修改操作"):
            approval.request_changes(step_id, approver_id, "comment")

        # 設置正確狀態
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = uuid.uuid4()  # 不同的步驟ID

        # 測試錯誤步驟
        with pytest.raises(ApprovalValidationError, match="只能對當前步驟要求修改"):
            approval.request_changes(step_id, approver_id, "comment")

        # 設置正確步驟
        approval.current_step_id = step_id

        # 測試空審批者ID
        with pytest.raises(ApprovalValidationError, match="審批者ID不能為空"):
            approval.request_changes(step_id, None, "comment")

        # 測試空修改要求
        with pytest.raises(ApprovalValidationError, match="修改要求不能為空"):
            approval.request_changes(step_id, approver_id, "")

    def test_progress_to_next_step(self):
        """測試進入下一個審批步驟"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        current_step_id = uuid.uuid4()
        next_step_id = uuid.uuid4()
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = current_step_id

        # Act
        approval.progress_to_next_step(next_step_id)

        # Assert
        assert approval.current_step_id == next_step_id

        events = approval.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalStepCompleted)
        assert events[0].step_id == current_step_id
        assert events[0].next_step_id == next_step_id

    def test_progress_to_next_step_completion(self):
        """測試進入下一步時完成審批"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        current_step_id = uuid.uuid4()
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = current_step_id

        # Act - 沒有下一步，應該完成審批
        approval.progress_to_next_step(None)

        # Assert
        assert approval.status == ApprovalStatus.APPROVED
        assert approval.completed_at is not None
        assert approval.current_step_id is None

        events = approval.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowCompleted)

    def test_progress_to_next_step_validation(self):
        """測試進入下一步的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        current_step_id = uuid.uuid4()

        # 測試無效狀態
        approval.status = ApprovalStatus.PENDING
        with pytest.raises(ApprovalStateError, match="無法在 pending 狀態下推進步驟"):
            approval.progress_to_next_step(uuid.uuid4())

        # 設置正確狀態
        approval.status = ApprovalStatus.IN_PROGRESS
        approval.current_step_id = current_step_id

        # 測試相同步驟ID
        with pytest.raises(ApprovalValidationError, match="下一步驟不能與當前步驟相同"):
            approval.progress_to_next_step(current_step_id)

    def test_complete_approval(self):
        """測試完成審批"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        approval.status = ApprovalStatus.IN_PROGRESS
        completed_by = uuid.uuid4()

        # Act
        approval.complete_approval(completed_by)

        # Assert
        assert approval.status == ApprovalStatus.APPROVED
        assert approval.completed_at is not None
        assert approval.current_step_id is None

        events = approval.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowCompleted)
        assert events[0].completed_by == completed_by

    def test_complete_approval_validation(self):
        """測試完成審批的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試無效狀態
        approval.status = ApprovalStatus.PENDING
        with pytest.raises(ApprovalStateError, match="無法從 pending 狀態完成審批"):
            approval.complete_approval()

    def test_cancel(self):
        """測試取消審批"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        approval.status = ApprovalStatus.IN_PROGRESS
        cancelled_by = uuid.uuid4()

        # Act
        approval.cancel(cancelled_by)

        # Assert
        assert approval.status == ApprovalStatus.CANCELLED
        assert approval.completed_at is not None
        assert approval.current_step_id is None

        events = approval.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowCompleted)
        assert events[0].completed_by == cancelled_by

    def test_cancel_validation(self):
        """測試取消審批的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試無效狀態
        approval.status = ApprovalStatus.APPROVED
        with pytest.raises(ApprovalStateError, match="無法從 approved 狀態取消審批"):
            approval.cancel(uuid.uuid4())

        # 測試空取消者ID
        approval.status = ApprovalStatus.IN_PROGRESS
        with pytest.raises(ApprovalValidationError, match="取消者ID不能為空"):
            approval.cancel(None)

    def test_reset_for_resubmission(self):
        """測試重置審批以便重新提交"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        approval.status = ApprovalStatus.REQUIRES_CHANGES
        approval.completed_at = datetime.now()
        approval.current_step_id = uuid.uuid4()

        new_workflow_id = uuid.uuid4()

        # Act
        approval.reset_for_resubmission(new_workflow_id)

        # Assert
        assert approval.status == ApprovalStatus.PENDING
        assert approval.completed_at is None
        assert approval.current_step_id is None
        assert approval.workflow_id == new_workflow_id

    def test_reset_for_resubmission_validation(self):
        """測試重置審批的驗證"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試無效狀態
        approval.status = ApprovalStatus.APPROVED
        with pytest.raises(ApprovalStateError, match="無法從 approved 狀態重置審批"):
            approval.reset_for_resubmission()

    def test_status_check_methods(self):
        """測試狀態檢查方法"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試 PENDING 狀態
        assert approval.is_in_progress() is False
        assert approval.is_completed() is False
        assert approval.is_pending_changes() is False

        # 測試 IN_PROGRESS 狀態
        approval.status = ApprovalStatus.IN_PROGRESS
        assert approval.is_in_progress() is True
        assert approval.is_completed() is False
        assert approval.is_pending_changes() is False

        # 測試 APPROVED 狀態
        approval.status = ApprovalStatus.APPROVED
        assert approval.is_in_progress() is False
        assert approval.is_completed() is True
        assert approval.is_pending_changes() is False

        # 測試 REQUIRES_CHANGES 狀態
        approval.status = ApprovalStatus.REQUIRES_CHANGES
        assert approval.is_in_progress() is False
        assert approval.is_completed() is False
        assert approval.is_pending_changes() is True

    def test_get_duration(self):
        """測試獲取審批持續時間"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試未完成的審批
        assert approval.get_duration() is None

        # 測試已完成的審批
        approval.completed_at = approval.submitted_at + timedelta(hours=2)
        duration = approval.get_duration()
        assert duration == 7200  # 2小時 = 7200秒

    def test_get_current_step_duration(self):
        """測試獲取當前步驟持續時間"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試沒有當前步驟
        assert approval.get_current_step_duration() is None

        # 測試有當前步驟
        approval.current_step_id = uuid.uuid4()
        duration = approval.get_current_step_duration()
        assert isinstance(duration, int)
        assert duration >= 0

    def test_validate_approval_state(self):
        """測試驗證審批狀態"""
        # 測試有效狀態
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )
        errors = approval.validate_approval_state()
        assert errors == []

        # 測試無效狀態
        invalid_approval = DocumentApproval(
            id=uuid.uuid4(),
            document_id=None,  # 空文檔ID
            workflow_id=None,  # 空工作流ID
            submitted_by=None,  # 空提交者ID
            status=ApprovalStatus.IN_PROGRESS,
            current_step_id=None  # 進行中但沒有當前步驟
        )

        errors = invalid_approval.validate_approval_state()
        assert "文檔ID不能為空" in errors
        assert "工作流ID不能為空" in errors
        assert "提交者ID不能為空" in errors
        assert "進行中的審批必須有當前步驟" in errors

    def test_state_transitions(self):
        """測試狀態轉換"""
        # Arrange
        approval = DocumentApproval.create(
            document_id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            submitted_by=uuid.uuid4()
        )

        # 測試有效轉換
        assert approval._can_transition_to(ApprovalStatus.IN_PROGRESS) is True
        assert approval._can_transition_to(ApprovalStatus.CANCELLED) is True
        assert approval._can_transition_to(ApprovalStatus.APPROVED) is False

        # 改變狀態並測試
        approval.status = ApprovalStatus.IN_PROGRESS
        assert approval._can_transition_to(ApprovalStatus.APPROVED) is True
        assert approval._can_transition_to(ApprovalStatus.REJECTED) is True
        assert approval._can_transition_to(ApprovalStatus.REQUIRES_CHANGES) is True
        assert approval._can_transition_to(ApprovalStatus.PENDING) is False

        # 測試終態
        approval.status = ApprovalStatus.APPROVED
        assert approval._can_transition_to(ApprovalStatus.IN_PROGRESS) is False
        assert approval._can_transition_to(ApprovalStatus.REJECTED) is False