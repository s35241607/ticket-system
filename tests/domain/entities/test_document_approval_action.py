import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock

from src.domain.entities.document_approval_action import DocumentApprovalAction, ActionValidationError
from src.domain.value_objects.approval_action_type import ApprovalActionType
from src.domain.events.document_approval_events import ApprovalActionCreated


class TestDocumentApprovalAction:
    """文檔審批行為實體測試"""

    def test_create_approval_action(self):
        """測試創建審批行為記錄"""
        # Arrange
        approval_id = uuid.uuid4()
        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()
        action_type = ApprovalActionType.APPROVE
        comment = "批准此文檔"
        metadata = {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}

        # Act
        action = DocumentApprovalAction.create_approval_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            action_type=action_type,
            comment=comment,
            metadata=metadata
        )

        # Assert
        assert action.approval_id == approval_id
        assert action.step_id == step_id
        assert action.approver_id == approver_id
        assert action.action_type == action_type
        assert action.comment == comment.strip()
        assert action.metadata == metadata
        assert isinstance(action.id, uuid.UUID)
        assert isinstance(action.created_at, datetime)

        # 檢查事件
        events = action.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalActionCreated)
        assert events[0].action_id == action.id
        assert events[0].approval_id == approval_id
        assert events[0].step_id == step_id
        assert events[0].approver_id == approver_id
        assert events[0].action_type == action_type.value
        assert events[0].comment == comment.strip()

    def test_create_approval_action_with_invalid_data(self):
        """測試使用無效數據創建審批行為"""
        approval_id = uuid.uuid4()
        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()

        # 測試空審批ID
        with pytest.raises(ActionValidationError, match="審批ID不能為空"):
            DocumentApprovalAction.create_approval_action(
                approval_id=None,
                step_id=step_id,
                approver_id=approver_id,
                action_type=ApprovalActionType.APPROVE,
                comment="comment"
            )

        # 測試空步驟ID
        with pytest.raises(ActionValidationError, match="步驟ID不能為空"):
            DocumentApprovalAction.create_approval_action(
                approval_id=approval_id,
                step_id=None,
                approver_id=approver_id,
                action_type=ApprovalActionType.APPROVE,
                comment="comment"
            )

        # 測試空審批者ID
        with pytest.raises(ActionValidationError, match="審批者ID不能為空"):
            DocumentApprovalAction.create_approval_action(
                approval_id=approval_id,
                step_id=step_id,
                approver_id=None,
                action_type=ApprovalActionType.APPROVE,
                comment="comment"
            )

        # 測試空評論
        with pytest.raises(ActionValidationError, match="評論不能為空"):
            DocumentApprovalAction.create_approval_action(
                approval_id=approval_id,
                step_id=step_id,
                approver_id=approver_id,
                action_type=ApprovalActionType.APPROVE,
                comment=""
            )

        # 測試評論過長
        long_comment = "a" * 2001
        with pytest.raises(ActionValidationError, match="評論不能超過2000個字符"):
            DocumentApprovalAction.create_approval_action(
                approval_id=approval_id,
                step_id=step_id,
                approver_id=approver_id,
                action_type=ApprovalActionType.APPROVE,
                comment=long_comment
            )

    def test_create_approve_action(self):
        """測試創建批准行為記錄"""
        # Arrange
        approval_id = uuid.uuid4()
        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()
        comment = "批准此文檔"
        metadata = {"reason": "符合標準"}

        # Act
        action = DocumentApprovalAction.create_approve_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            comment=comment,
            metadata=metadata
        )

        # Assert
        assert action.action_type == ApprovalActionType.APPROVE
        assert action.comment == comment
        assert action.metadata == metadata

    def test_create_reject_action(self):
        """測試創建拒絕行為記錄"""
        # Arrange
        approval_id = uuid.uuid4()
        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()
        comment = "不符合要求"
        metadata = {"reason": "內容不完整"}

        # Act
        action = DocumentApprovalAction.create_reject_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            comment=comment,
            metadata=metadata
        )

        # Assert
        assert action.action_type == ApprovalActionType.REJECT
        assert action.comment == comment
        assert action.metadata == metadata

    def test_create_request_changes_action(self):
        """測試創建要求修改行為記錄"""
        # Arrange
        approval_id = uuid.uuid4()
        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()
        comment = "需要修改格式"
        metadata = {"changes_required": ["格式", "內容"]}

        # Act
        action = DocumentApprovalAction.create_request_changes_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            comment=comment,
            metadata=metadata
        )

        # Assert
        assert action.action_type == ApprovalActionType.REQUEST_CHANGES
        assert action.comment == comment
        assert action.metadata == metadata

    def test_create_escalate_action(self):
        """測試創建升級行為記錄"""
        # Arrange
        approval_id = uuid.uuid4()
        step_id = uuid.uuid4()
        approver_id = uuid.uuid4()
        escalated_to = uuid.uuid4()
        comment = "升級至高級審批者"
        metadata = {"reason": "超時"}

        # Act
        action = DocumentApprovalAction.create_escalate_action(
            approval_id=approval_id,
            step_id=step_id,
            approver_id=approver_id,
            comment=comment,
            escalated_to=escalated_to,
            metadata=metadata
        )

        # Assert
        assert action.action_type == ApprovalActionType.ESCALATE
        assert action.comment == comment
        assert action.get_escalated_to() == escalated_to
        assert action.metadata["escalated_to"] == str(escalated_to)
        assert action.metadata["reason"] == "超時"

    def test_create_auto_approve_action(self):
        """測試創建自動批准行為記錄"""
        # Arrange
        approval_id = uuid.uuid4()
        step_id = uuid.uuid4()
        system_user_id = uuid.uuid4()
        comment = "超時自動批准"
        timeout_hours = 24
        metadata = {"trigger": "timeout"}

        # Act
        action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=approval_id,
            step_id=step_id,
            system_user_id=system_user_id,
            comment=comment,
            timeout_hours=timeout_hours,
            metadata=metadata
        )

        # Assert
        assert action.action_type == ApprovalActionType.AUTO_APPROVE
        assert action.comment == comment
        assert action.is_system_action() is True
        assert action.is_timeout_action() is True
        assert action.get_timeout_hours() == timeout_hours
        assert action.metadata["is_system_action"] is True
        assert action.metadata["timeout_hours"] == timeout_hours
        assert action.metadata["trigger"] == "timeout"

    def test_is_system_action(self):
        """測試檢查是否為系統行為"""
        # 測試非系統行為
        action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )
        assert action.is_system_action() is False

        # 測試系統行為
        system_action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            system_user_id=uuid.uuid4(),
            comment="自動批准"
        )
        assert system_action.is_system_action() is True

    def test_is_escalation_action(self):
        """測試檢查是否為升級行為"""
        # 測試非升級行為
        action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )
        assert action.is_escalation_action() is False

        # 測試升級行為
        escalate_action = DocumentApprovalAction.create_escalate_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="升級",
            escalated_to=uuid.uuid4()
        )
        assert escalate_action.is_escalation_action() is True

    def test_is_timeout_action(self):
        """測試檢查是否為超時相關行為"""
        # 測試非超時行為
        action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )
        assert action.is_timeout_action() is False

        # 測試超時自動批准行為
        timeout_action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            system_user_id=uuid.uuid4(),
            comment="超時自動批准",
            timeout_hours=24
        )
        assert timeout_action.is_timeout_action() is True

        # 測試非超時的自動批准行為
        non_timeout_auto_action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            system_user_id=uuid.uuid4(),
            comment="自動批准"
        )
        assert non_timeout_auto_action.is_timeout_action() is False

    def test_get_escalated_to(self):
        """測試獲取升級目標審批者"""
        # 測試非升級行為
        action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )
        assert action.get_escalated_to() is None

        # 測試升級行為
        escalated_to = uuid.uuid4()
        escalate_action = DocumentApprovalAction.create_escalate_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="升級",
            escalated_to=escalated_to
        )
        assert escalate_action.get_escalated_to() == escalated_to

        # 測試沒有升級目標的升級行為
        escalate_action_no_target = DocumentApprovalAction.create_escalate_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="升級"
        )
        assert escalate_action_no_target.get_escalated_to() is None

    def test_get_timeout_hours(self):
        """測試獲取超時小時數"""
        # 測試非超時行為
        action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )
        assert action.get_timeout_hours() is None

        # 測試超時行為
        timeout_hours = 48
        timeout_action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            system_user_id=uuid.uuid4(),
            comment="超時自動批准",
            timeout_hours=timeout_hours
        )
        assert timeout_action.get_timeout_hours() == timeout_hours

    def test_add_and_get_metadata(self):
        """測試添加和獲取元數據"""
        # Arrange
        action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )

        # Act
        action.add_metadata("custom_field", "custom_value")
        action.add_metadata("number_field", 123)

        # Assert
        assert action.get_metadata("custom_field") == "custom_value"
        assert action.get_metadata("number_field") == 123
        assert action.get_metadata("non_existent", "default") == "default"

    def test_add_metadata_validation(self):
        """測試添加元數據的驗證"""
        # Arrange
        action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )

        # 測試空鍵
        with pytest.raises(ActionValidationError, match="元數據鍵不能為空"):
            action.add_metadata("", "value")

        with pytest.raises(ActionValidationError, match="元數據鍵不能為空"):
            action.add_metadata("   ", "value")

    def test_get_action_summary(self):
        """測試獲取行為摘要"""
        # 測試普通批准行為
        approve_action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准"
        )
        assert approve_action.get_action_summary() == "批准"

        # 測試拒絕行為
        reject_action = DocumentApprovalAction.create_reject_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="拒絕"
        )
        assert reject_action.get_action_summary() == "拒絕"

        # 測試要求修改行為
        changes_action = DocumentApprovalAction.create_request_changes_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="要求修改"
        )
        assert changes_action.get_action_summary() == "要求修改"

        # 測試升級行為
        escalated_to = uuid.uuid4()
        escalate_action = DocumentApprovalAction.create_escalate_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="升級",
            escalated_to=escalated_to
        )
        assert escalate_action.get_action_summary() == f"升級至 {escalated_to}"

        # 測試沒有目標的升級行為
        escalate_action_no_target = DocumentApprovalAction.create_escalate_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="升級"
        )
        assert escalate_action_no_target.get_action_summary() == "升級"

        # 測試系統自動批准行為
        system_action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            system_user_id=uuid.uuid4(),
            comment="自動批准"
        )
        assert system_action.get_action_summary() == "系統自動批准"

        # 測試超時自動批准行為
        timeout_action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            system_user_id=uuid.uuid4(),
            comment="超時自動批准",
            timeout_hours=24
        )
        assert timeout_action.get_action_summary() == "超時自動批准（24小時）"

    def test_validate_action(self):
        """測試驗證行為記錄"""
        # 測試有效行為
        valid_action = DocumentApprovalAction.create_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="批准此文檔"
        )
        errors = valid_action.validate_action()
        assert errors == []

        # 測試無效行為
        invalid_action = DocumentApprovalAction(
            id=uuid.uuid4(),
            approval_id=None,  # 空審批ID
            step_id=None,  # 空步驟ID
            approver_id=None,  # 空審批者ID
            action_type=ApprovalActionType.APPROVE,
            comment="",  # 空評論
            metadata={}
        )

        errors = invalid_action.validate_action()
        assert "審批ID不能為空" in errors
        assert "步驟ID不能為空" in errors
        assert "審批者ID不能為空" in errors
        assert "評論不能為空" in errors

        # 測試評論過長
        long_comment_action = DocumentApprovalAction(
            id=uuid.uuid4(),
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            action_type=ApprovalActionType.APPROVE,
            comment="a" * 2001,  # 超長評論
            metadata={}
        )

        errors = long_comment_action.validate_action()
        assert "評論不能超過2000個字符" in errors

    def test_validate_escalation_action(self):
        """測試驗證升級行為"""
        # 測試有效升級行為
        valid_escalate_action = DocumentApprovalAction.create_escalate_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            comment="升級",
            escalated_to=uuid.uuid4()
        )
        errors = valid_escalate_action.validate_action()
        assert errors == []

        # 測試無效升級行為（沒有升級目標）
        invalid_escalate_action = DocumentApprovalAction(
            id=uuid.uuid4(),
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            action_type=ApprovalActionType.ESCALATE,
            comment="升級",
            metadata={}  # 沒有升級目標
        )

        errors = invalid_escalate_action.validate_action()
        assert "升級行為必須指定升級目標" in errors

    def test_validate_auto_approve_action(self):
        """測試驗證自動批准行為"""
        # 測試有效自動批准行為
        valid_auto_action = DocumentApprovalAction.create_auto_approve_action(
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            system_user_id=uuid.uuid4(),
            comment="自動批准"
        )
        errors = valid_auto_action.validate_action()
        assert errors == []

        # 測試無效自動批准行為（沒有系統標記）
        invalid_auto_action = DocumentApprovalAction(
            id=uuid.uuid4(),
            approval_id=uuid.uuid4(),
            step_id=uuid.uuid4(),
            approver_id=uuid.uuid4(),
            action_type=ApprovalActionType.AUTO_APPROVE,
            comment="自動批准",
            metadata={}  # 沒有系統標記
        )

        errors = invalid_auto_action.validate_action()
        assert "自動批准行為必須標記為系統行為" in errors