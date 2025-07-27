import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.domain.entities.document_approval_step import DocumentApprovalStep, StepValidationError
from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.domain.value_objects.approver_type import ApproverType
from src.domain.events.document_approval_events import (
    ApprovalStepCreated, ApprovalStepUpdated, ApprovalTimeoutOccurred
)


class TestDocumentApprovalStep:
    """文檔審批步驟實體測試"""

    def test_create_individual_step(self):
        """測試創建個人審批步驟"""
        # Arrange
        workflow_id = uuid.uuid4()
        name = "個人審批步驟"
        description = "這是一個個人審批步驟"
        order = 1
        approver_type = ApproverType.INDIVIDUAL
        user_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        approver_criteria = {"user_ids": user_ids}

        # Act
        step = DocumentApprovalStep.create(
            workflow_id=workflow_id,
            name=name,
            description=description,
            order=order,
            approver_type=approver_type,
            approver_criteria=approver_criteria
        )

        # Assert
        assert step.workflow_id == workflow_id
        assert step.name == name
        assert step.description == description
        assert step.order == order
        assert step.approver_type == approver_type
        assert step.approver_criteria == approver_criteria
        assert step.is_parallel is False
        assert step.timeout_hours is None
        assert step.auto_approve_on_timeout is False
        assert isinstance(step.id, uuid.UUID)
        assert isinstance(step.created_at, datetime)

        # 檢查事件
        events = step.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalStepCreated)
        assert events[0].step_id == step.id
        assert events[0].workflow_id == workflow_id
        assert events[0].name == name
        assert events[0].order == order
        assert events[0].approver_type == approver_type.value
        assert events[0].is_parallel is False

    def test_create_role_step(self):
        """測試創建角色審批步驟"""
        # Arrange
        workflow_id = uuid.uuid4()
        approver_criteria = {"roles": ["manager", "supervisor"]}

        # Act
        step = DocumentApprovalStep.create(
            workflow_id=workflow_id,
            name="角色審批步驟",
            description="基於角色的審批步驟",
            order=1,
            approver_type=ApproverType.ROLE,
            approver_criteria=approver_criteria,
            is_parallel=True
        )

        # Assert
        assert step.approver_type == ApproverType.ROLE
        assert step.approver_criteria == approver_criteria
        assert step.is_parallel is True

    def test_create_department_step(self):
        """測試創建部門審批步驟"""
        # Arrange
        workflow_id = uuid.uuid4()
        department_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        approver_criteria = {"department_ids": department_ids}

        # Act
        step = DocumentApprovalStep.create(
            workflow_id=workflow_id,
            name="部門審批步驟",
            description="基於部門的審批步驟",
            order=1,
            approver_type=ApproverType.DEPARTMENT,
            approver_criteria=approver_criteria
        )

        # Assert
        assert step.approver_type == ApproverType.DEPARTMENT
        assert step.approver_criteria == approver_criteria

    def test_create_creator_manager_step(self):
        """測試創建創建者主管審批步驟"""
        # Arrange
        workflow_id = uuid.uuid4()
        approver_criteria = {}  # 創建者主管類型不需要額外條件

        # Act
        step = DocumentApprovalStep.create(
            workflow_id=workflow_id,
            name="主管審批步驟",
            description="創建者主管審批步驟",
            order=1,
            approver_type=ApproverType.CREATOR_MANAGER,
            approver_criteria=approver_criteria
        )

        # Assert
        assert step.approver_type == ApproverType.CREATOR_MANAGER
        assert step.approver_criteria == approver_criteria

    def test_create_step_with_timeout(self):
        """測試創建帶超時的審批步驟"""
        # Arrange
        workflow_id = uuid.uuid4()
        timeout_hours = 24
        approver_criteria = {"user_ids": [str(uuid.uuid4())]}

        # Act
        step = DocumentApprovalStep.create(
            workflow_id=workflow_id,
            name="超時審批步驟",
            description="帶超時的審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria=approver_criteria,
            timeout_hours=timeout_hours,
            auto_approve_on_timeout=True
        )

        # Assert
        assert step.timeout_hours == timeout_hours
        assert step.auto_approve_on_timeout is True

    def test_create_step_with_invalid_data(self):
        """測試使用無效數據創建步驟"""
        workflow_id = uuid.uuid4()

        # 測試空名稱
        with pytest.raises(StepValidationError, match="步驟名稱不能為空"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="",
                description="描述",
                order=1,
                approver_type=ApproverType.INDIVIDUAL,
                approver_criteria={"user_ids": [str(uuid.uuid4())]}
            )

        # 測試空描述
        with pytest.raises(StepValidationError, match="步驟描述不能為空"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="",
                order=1,
                approver_type=ApproverType.INDIVIDUAL,
                approver_criteria={"user_ids": [str(uuid.uuid4())]}
            )

        # 測試無效順序
        with pytest.raises(StepValidationError, match="步驟順序必須大於0"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="描述",
                order=0,
                approver_type=ApproverType.INDIVIDUAL,
                approver_criteria={"user_ids": [str(uuid.uuid4())]}
            )

        # 測試空審批者條件
        with pytest.raises(StepValidationError, match="審批者條件不能為空"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="描述",
                order=1,
                approver_type=ApproverType.INDIVIDUAL,
                approver_criteria={}
            )

        # 測試無效超時時間
        with pytest.raises(StepValidationError, match="超時時間必須大於0"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="描述",
                order=1,
                approver_type=ApproverType.INDIVIDUAL,
                approver_criteria={"user_ids": [str(uuid.uuid4())]},
                timeout_hours=0
            )

    def test_validate_approver_criteria(self):
        """測試審批者條件驗證"""
        workflow_id = uuid.uuid4()

        # 測試個人審批者缺少 user_ids
        with pytest.raises(StepValidationError, match="個人審批者類型必須包含 user_ids"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="描述",
                order=1,
                approver_type=ApproverType.INDIVIDUAL,
                approver_criteria={"invalid_key": "value"}
            )

        # 測試個人審批者 user_ids 為空
        with pytest.raises(StepValidationError, match="user_ids 必須是非空列表"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="描述",
                order=1,
                approver_type=ApproverType.INDIVIDUAL,
                approver_criteria={"user_ids": []}
            )

        # 測試角色審批者缺少 roles
        with pytest.raises(StepValidationError, match="角色審批者類型必須包含 roles"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="描述",
                order=1,
                approver_type=ApproverType.ROLE,
                approver_criteria={"invalid_key": "value"}
            )

        # 測試部門審批者缺少 department_ids
        with pytest.raises(StepValidationError, match="部門審批者類型必須包含 department_ids"):
            DocumentApprovalStep.create(
                workflow_id=workflow_id,
                name="名稱",
                description="描述",
                order=1,
                approver_type=ApproverType.DEPARTMENT,
                approver_criteria={"invalid_key": "value"}
            )

    def test_resolve_approvers_individual(self):
        """測試解析個人審批者"""
        # Arrange
        user_id1 = uuid.uuid4()
        user_id2 = uuid.uuid4()
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="個人審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(user_id1), str(user_id2)]}
        )

        document = Document.create(
            title="測試文檔",
            content="內容",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )

        # Act
        approvers = step.resolve_approvers(document)

        # Assert
        assert len(approvers) == 2
        assert user_id1 in approvers
        assert user_id2 in approvers

    def test_resolve_approvers_invalid_uuid(self):
        """測試解析無效UUID的審批者"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="個人審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": ["invalid-uuid"]}
        )

        document = Document.create(
            title="測試文檔",
            content="內容",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )

        # Act & Assert
        with pytest.raises(StepValidationError, match="無效的用戶ID格式"):
            step.resolve_approvers(document)

    def test_is_timeout_exceeded(self):
        """測試超時檢查"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="超時步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            timeout_hours=2
        )

        # 測試未超時
        recent_time = datetime.now() - timedelta(hours=1)
        assert step.is_timeout_exceeded(recent_time) is False

        # 測試已超時
        old_time = datetime.now() - timedelta(hours=3)
        assert step.is_timeout_exceeded(old_time) is True

        # 測試沒有設置超時
        step_no_timeout = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="無超時步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        assert step_no_timeout.is_timeout_exceeded(old_time) is False

    def test_get_timeout_deadline(self):
        """測試獲取超時截止時間"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="超時步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            timeout_hours=24
        )

        approval_time = datetime.now()

        # Act
        deadline = step.get_timeout_deadline(approval_time)

        # Assert
        expected_deadline = approval_time + timedelta(hours=24)
        assert deadline == expected_deadline

        # 測試沒有超時設置
        step_no_timeout = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="無超時步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        assert step_no_timeout.get_timeout_deadline(approval_time) is None

    def test_can_approve(self):
        """測試檢查用戶是否可以審批"""
        # Arrange
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="個人審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(user_id)]}
        )

        document = Document.create(
            title="測試文檔",
            content="內容",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )

        # Act & Assert
        assert step.can_approve(user_id, document) is True
        assert step.can_approve(other_user_id, document) is False

    def test_update_approver_criteria(self):
        """測試更新審批者條件"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="個人審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        new_user_id = uuid.uuid4()
        new_criteria = {"user_ids": [str(new_user_id)]}

        # 清空創建事件
        step.get_events()

        # Act
        step.update_approver_criteria(new_criteria)

        # Assert
        assert step.approver_criteria == new_criteria

        # 檢查事件
        events = step.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalStepUpdated)
        assert events[0].step_id == step.id

    def test_update_approver_criteria_validation(self):
        """測試更新審批者條件的驗證"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="個人審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        # 測試空條件
        with pytest.raises(StepValidationError, match="審批者條件不能為空"):
            step.update_approver_criteria({})

        # 測試無效條件
        with pytest.raises(StepValidationError, match="個人審批者類型必須包含 user_ids"):
            step.update_approver_criteria({"invalid_key": "value"})

    def test_update_timeout_settings(self):
        """測試更新超時設置"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        # 清空創建事件
        step.get_events()

        # Act
        step.update_timeout_settings(timeout_hours=48, auto_approve_on_timeout=True)

        # Assert
        assert step.timeout_hours == 48
        assert step.auto_approve_on_timeout is True

        # 檢查事件
        events = step.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalStepUpdated)

    def test_update_timeout_settings_validation(self):
        """測試更新超時設置的驗證"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        # 測試無效超時時間
        with pytest.raises(StepValidationError, match="超時時間必須大於0"):
            step.update_timeout_settings(timeout_hours=0)

    def test_handle_timeout(self):
        """測試處理步驟超時"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="超時步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            timeout_hours=24
        )

        approval_id = uuid.uuid4()

        # 清空創建事件
        step.get_events()

        # Act
        step.handle_timeout(approval_id)

        # Assert
        events = step.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalTimeoutOccurred)
        assert events[0].approval_id == approval_id
        assert events[0].step_id == step.id
        assert events[0].timeout_hours == 24
        assert events[0].escalation_required is True

    def test_handle_timeout_with_auto_approve(self):
        """測試處理帶自動批准的步驟超時"""
        # Arrange
        step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="自動批准超時步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            timeout_hours=24,
            auto_approve_on_timeout=True
        )

        approval_id = uuid.uuid4()

        # 清空創建事件
        step.get_events()

        # Act
        step.handle_timeout(approval_id)

        # Assert
        events = step.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalTimeoutOccurred)
        assert events[0].escalation_required is False

    def test_get_required_approver_count(self):
        """測試獲取所需審批者數量"""
        # 測試個人審批者
        step_individual = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="個人審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4()), str(uuid.uuid4())]}
        )
        assert step_individual.get_required_approver_count() == 2

        # 測試帶最小審批者數量的步驟
        step_with_min = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="角色審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.ROLE,
            approver_criteria={"roles": ["manager"], "min_approvers": 3}
        )
        assert step_with_min.get_required_approver_count() == 3

        # 測試默認情況
        step_default = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="角色審批步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.ROLE,
            approver_criteria={"roles": ["manager"]}
        )
        assert step_default.get_required_approver_count() == 1

    def test_is_sequential_step(self):
        """測試檢查是否為順序步驟"""
        # 測試順序步驟
        sequential_step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="順序步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            is_parallel=False
        )
        assert sequential_step.is_sequential_step() is True

        # 測試並行步驟
        parallel_step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="並行步驟",
            description="描述",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            is_parallel=True
        )
        assert parallel_step.is_sequential_step() is False

    def test_validate_step_configuration(self):
        """測試驗證步驟配置"""
        # 測試有效配置
        valid_step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),
            name="有效步驟",
            description="有效的審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            timeout_hours=24
        )
        errors = valid_step.validate_step_configuration()
        assert errors == []

        # 測試無效配置
        invalid_step = DocumentApprovalStep(
            id=uuid.uuid4(),
            workflow_id=uuid.uuid4(),
            name="",  # 空名稱
            description="",  # 空描述
            order=0,  # 無效順序
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={},  # 空條件
            timeout_hours=-1  # 無效超時
        )

        errors = invalid_step.validate_step_configuration()
        assert "步驟名稱不能為空" in errors
        assert "步驟描述不能為空" in errors
        assert "步驟順序必須大於0" in errors
        assert "審批者條件不能為空" in errors
        assert "超時時間必須大於0" in errors