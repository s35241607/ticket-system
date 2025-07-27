import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock

from src.domain.entities.document_approval_workflow import DocumentApprovalWorkflow, WorkflowValidationError
from src.domain.entities.document_approval_step import DocumentApprovalStep
from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.domain.value_objects.approver_type import ApproverType
from src.domain.events.document_approval_events import (
    ApprovalWorkflowCreated, ApprovalWorkflowUpdated,
    ApprovalWorkflowActivated, ApprovalWorkflowDeactivated
)


class TestDocumentApprovalWorkflow:
    """文檔審批工作流實體測試"""

    def test_create_workflow(self):
        """測試創建工作流"""
        # Arrange
        name = "測試工作流"
        description = "這是一個測試工作流"
        category_criteria = {"equals": "technical"}
        tag_criteria = {"contains_any": ["urgent", "important"]}
        creator_criteria = {"department": "engineering"}

        # Act
        workflow = DocumentApprovalWorkflow.create(
            name=name,
            description=description,
            category_criteria=category_criteria,
            tag_criteria=tag_criteria,
            creator_criteria=creator_criteria
        )

        # Assert
        assert workflow.name == name
        assert workflow.description == description
        assert workflow.category_criteria == category_criteria
        assert workflow.tag_criteria == tag_criteria
        assert workflow.creator_criteria == creator_criteria
        assert workflow.is_active is True
        assert isinstance(workflow.id, uuid.UUID)
        assert isinstance(workflow.created_at, datetime)
        assert isinstance(workflow.updated_at, datetime)
        assert workflow.steps == []

        # 檢查事件
        events = workflow.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowCreated)
        assert events[0].workflow_id == workflow.id
        assert events[0].name == name
        assert events[0].description == description

    def test_create_workflow_with_invalid_data(self):
        """測試使用無效數據創建工作流"""
        # 測試空名稱
        with pytest.raises(WorkflowValidationError, match="工作流名稱不能為空"):
            DocumentApprovalWorkflow.create("", "描述")

        # 測試空描述
        with pytest.raises(WorkflowValidationError, match="工作流描述不能為空"):
            DocumentApprovalWorkflow.create("名稱", "")

        # 測試名稱過長
        long_name = "a" * 201
        with pytest.raises(WorkflowValidationError, match="工作流名稱不能超過200個字符"):
            DocumentApprovalWorkflow.create(long_name, "描述")

        # 測試描述過長
        long_description = "a" * 1001
        with pytest.raises(WorkflowValidationError, match="工作流描述不能超過1000個字符"):
            DocumentApprovalWorkflow.create("名稱", long_description)

    def test_add_step(self):
        """測試添加審批步驟"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        # 清空創建事件
        workflow.get_events()

        # Act
        workflow.add_step(step)

        # Assert
        assert len(workflow.steps) == 1
        assert workflow.steps[0] == step

        # 檢查事件
        events = workflow.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowUpdated)
        assert events[0].workflow_id == workflow.id

    def test_add_step_validation(self):
        """測試添加步驟的驗證"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        workflow.deactivate()

        step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        # 測試向非活動工作流添加步驟
        with pytest.raises(WorkflowValidationError, match="無法向非活動工作流添加步驟"):
            workflow.add_step(step)

        # 手動添加步驟以便重新啟用工作流
        workflow.steps.append(step)
        workflow.activate()

        # 測試添加重複步驟
        with pytest.raises(WorkflowValidationError, match="步驟已存在於工作流中"):
            workflow.add_step(step)

        # 測試添加相同順序的步驟
        duplicate_order_step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="重複順序步驟",
            description="重複順序的步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        with pytest.raises(WorkflowValidationError, match="步驟順序 1 已被使用"):
            workflow.add_step(duplicate_order_step)

        # 測試添加不屬於此工作流的步驟
        other_workflow_step = DocumentApprovalStep.create(
            workflow_id=uuid.uuid4(),  # 不同的工作流ID
            name="其他工作流步驟",
            description="屬於其他工作流的步驟",
            order=2,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        with pytest.raises(WorkflowValidationError, match="步驟不屬於此工作流"):
            workflow.add_step(other_workflow_step)

    def test_remove_step(self):
        """測試移除審批步驟"""
        # Arrange
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

        # 清空事件
        workflow.get_events()

        # Act
        workflow.remove_step(step.id)

        # Assert
        assert len(workflow.steps) == 0

        # 檢查事件
        events = workflow.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowUpdated)

    def test_remove_step_validation(self):
        """測試移除步驟的驗證"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        workflow.deactivate()

        # 測試從非活動工作流移除步驟
        with pytest.raises(WorkflowValidationError, match="無法從非活動工作流移除步驟"):
            workflow.remove_step(uuid.uuid4())

        # 手動添加步驟以便重新啟用工作流
        step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        workflow.steps.append(step)
        workflow.activate()

        # 測試移除不存在的步驟
        with pytest.raises(WorkflowValidationError, match="步驟不存在於工作流中"):
            workflow.remove_step(uuid.uuid4())

    def test_get_applicable_documents(self):
        """測試檢查工作流是否適用於文檔"""
        # Arrange
        category_id = uuid.uuid4()
        tag1 = uuid.uuid4()
        tag2 = uuid.uuid4()
        creator_id = uuid.uuid4()

        workflow = DocumentApprovalWorkflow.create(
            name="測試工作流",
            description="描述",
            category_criteria={"equals": str(category_id)},
            tag_criteria={"contains_any": [str(tag1), str(tag2)]},
            creator_criteria={"equals": str(creator_id)}
        )

        # 添加步驟使工作流有效
        step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        workflow.add_step(step)

        # 創建匹配的文檔
        matching_document = Document.create(
            title="測試文檔",
            content="內容",
            category_id=category_id,
            creator_id=creator_id,
            tags=[tag1]
        )

        # 創建不匹配的文檔
        non_matching_document = Document.create(
            title="不匹配文檔",
            content="內容",
            category_id=uuid.uuid4(),  # 不同的分類
            creator_id=creator_id,
            tags=[tag1]
        )

        # Act & Assert
        assert workflow.get_applicable_documents(matching_document) is True
        assert workflow.get_applicable_documents(non_matching_document) is False

        # 測試非活動工作流
        workflow.deactivate()
        assert workflow.get_applicable_documents(matching_document) is False

        # 測試沒有步驟的工作流
        workflow.activate()
        workflow.remove_step(step.id)
        assert workflow.get_applicable_documents(matching_document) is False

    def test_get_first_step(self):
        """測試獲取第一個審批步驟"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")

        # 測試沒有步驟的情況
        assert workflow.get_first_step() is None

        # 添加多個步驟
        step2 = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第二步",
            description="第二個審批步驟",
            order=2,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        step1 = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        workflow.add_step(step2)
        workflow.add_step(step1)

        # Act
        first_step = workflow.get_first_step()

        # Assert
        assert first_step == step1
        assert first_step.order == 1

    def test_get_next_step(self):
        """測試獲取下一個審批步驟"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")

        step1 = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        step2 = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第二步",
            description="第二個審批步驟",
            order=2,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        workflow.add_step(step1)
        workflow.add_step(step2)

        # Act & Assert
        next_step = workflow.get_next_step(step1.id)
        assert next_step == step2

        # 測試最後一步
        assert workflow.get_next_step(step2.id) is None

        # 測試不存在的步驟
        assert workflow.get_next_step(uuid.uuid4()) is None

    def test_activate_workflow(self):
        """測試啟用工作流"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        workflow.deactivate()

        step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )

        # 手動添加步驟（繞過活動狀態檢查）
        workflow.steps.append(step)

        # 清空事件
        workflow.get_events()

        # Act
        workflow.activate()

        # Assert
        assert workflow.is_active is True

        # 檢查事件
        events = workflow.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowActivated)

    def test_activate_workflow_validation(self):
        """測試啟用工作流的驗證"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        workflow.deactivate()

        # 測試啟用沒有步驟的工作流
        with pytest.raises(WorkflowValidationError, match="無法啟用沒有步驟的工作流"):
            workflow.activate()

    def test_deactivate_workflow(self):
        """測試停用工作流"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")

        # 清空創建事件
        workflow.get_events()

        # Act
        workflow.deactivate()

        # Assert
        assert workflow.is_active is False

        # 檢查事件
        events = workflow.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowDeactivated)

    def test_update_criteria(self):
        """測試更新工作流條件"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        new_category_criteria = {"equals": "new_category"}
        new_tag_criteria = {"contains_all": ["tag1", "tag2"]}

        # 清空創建事件
        workflow.get_events()

        # Act
        workflow.update_criteria(
            category_criteria=new_category_criteria,
            tag_criteria=new_tag_criteria
        )

        # Assert
        assert workflow.category_criteria == new_category_criteria
        assert workflow.tag_criteria == new_tag_criteria

        # 檢查事件
        events = workflow.get_events()
        assert len(events) == 1
        assert isinstance(events[0], ApprovalWorkflowUpdated)

    def test_validate_workflow(self):
        """測試工作流驗證"""
        # 測試有效工作流
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

        errors = workflow.validate_workflow()
        assert errors == []

        # 測試無效工作流
        invalid_workflow = DocumentApprovalWorkflow(
            id=uuid.uuid4(),
            name="",  # 空名稱
            description="",  # 空描述
            steps=[]  # 沒有步驟
        )

        errors = invalid_workflow.validate_workflow()
        assert "工作流名稱不能為空" in errors
        assert "工作流描述不能為空" in errors
        assert "工作流必須至少包含一個步驟" in errors

    def test_get_step_by_order(self):
        """測試根據順序獲取步驟"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")
        step1 = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="第一步",
            description="第一個審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]}
        )
        workflow.add_step(step1)

        # Act & Assert
        assert workflow.get_step_by_order(1) == step1
        assert workflow.get_step_by_order(2) is None

    def test_has_parallel_steps(self):
        """測試檢查是否包含並行步驟"""
        # Arrange
        workflow = DocumentApprovalWorkflow.create("測試工作流", "描述")

        # 添加順序步驟
        sequential_step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="順序步驟",
            description="順序審批步驟",
            order=1,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            is_parallel=False
        )
        workflow.add_step(sequential_step)

        # 測試沒有並行步驟
        assert workflow.has_parallel_steps() is False

        # 添加並行步驟
        parallel_step = DocumentApprovalStep.create(
            workflow_id=workflow.id,
            name="並行步驟",
            description="並行審批步驟",
            order=2,
            approver_type=ApproverType.INDIVIDUAL,
            approver_criteria={"user_ids": [str(uuid.uuid4())]},
            is_parallel=True
        )
        workflow.add_step(parallel_step)

        # 測試包含並行步驟
        assert workflow.has_parallel_steps() is True