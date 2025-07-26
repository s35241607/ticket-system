import pytest
import uuid
from unittest.mock import Mock, MagicMock

from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.domain.events.document_events import DocumentCreated, DocumentViewed
from src.application.use_cases.document_use_cases import (
    CreateDocumentUseCase, GetDocumentUseCase, UpdateDocumentUseCase,
    ListDocumentsUseCase, PublishDocumentUseCase, DeleteDocumentUseCase,
    AddDocumentTagUseCase
)


class TestCreateDocumentUseCase:
    """創建文檔用例測試"""
    
    def test_execute(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 模擬儲存庫的 save 方法返回文檔
        mock_repo.save.return_value = MagicMock(spec=Document)
        
        use_case = CreateDocumentUseCase(mock_repo, mock_event_publisher)
        
        title = "Test Document"
        content = "This is a test document"
        category_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        summary = "Test summary"
        tags = [uuid.uuid4()]
        
        # Act
        result = use_case.execute(
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id,
            summary=summary,
            tags=tags
        )
        
        # Assert
        assert result is not None
        mock_repo.save.assert_called_once()
        mock_event_publisher.publish_all.assert_called_once()


class TestGetDocumentUseCase:
    """獲取文檔用例測試"""
    
    def test_execute_document_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 創建一個模擬文檔
        mock_document = MagicMock(spec=Document)
        mock_repo.get_by_id.return_value = mock_document
        
        use_case = GetDocumentUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        viewer_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id, viewer_id)
        
        # Assert
        assert result is not None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.increment_view_count.assert_called_once()
        mock_repo.save.assert_called_once_with(mock_document)
        mock_event_publisher.publish.assert_called_once()
        
        # 檢查發布的事件類型
        event = mock_event_publisher.publish.call_args[0][0]
        assert isinstance(event, DocumentViewed)
        assert event.document_id == document_id
        assert event.viewer_id == viewer_id
    
    def test_execute_document_not_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 模擬文檔未找到
        mock_repo.get_by_id.return_value = None
        
        use_case = GetDocumentUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id)
        
        # Assert
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_repo.save.assert_not_called()
        mock_event_publisher.publish.assert_not_called()


class TestUpdateDocumentUseCase:
    """更新文檔用例測試"""
    
    def test_execute_document_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 創建一個模擬文檔
        mock_document = MagicMock(spec=Document)
        mock_repo.get_by_id.return_value = mock_document
        mock_repo.save.return_value = mock_document
        
        use_case = UpdateDocumentUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        title = "Updated Title"
        content = "Updated Content"
        
        # Act
        result = use_case.execute(document_id, title, content)
        
        # Assert
        assert result is not None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.update.assert_called_once_with(
            title=title,
            content=content,
            summary=None,
            category_id=None
        )
        mock_repo.save.assert_called_once_with(mock_document)
        mock_event_publisher.publish_all.assert_called_once()
    
    def test_execute_document_not_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 模擬文檔未找到
        mock_repo.get_by_id.return_value = None
        
        use_case = UpdateDocumentUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id, "Title", "Content")
        
        # Assert
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_repo.save.assert_not_called()
        mock_event_publisher.publish_all.assert_not_called()


class TestListDocumentsUseCase:
    """獲取文檔列表用例測試"""
    
    def test_execute(self):
        # Arrange
        mock_repo = Mock()
        
        # 創建模擬文檔列表
        mock_documents = [MagicMock(spec=Document) for _ in range(3)]
        mock_repo.list.return_value = mock_documents
        
        use_case = ListDocumentsUseCase(mock_repo)
        filters = {"category_id": uuid.uuid4()}
        skip = 0
        limit = 10
        
        # Act
        result = use_case.execute(filters, skip, limit)
        
        # Assert
        assert result == mock_documents
        mock_repo.list.assert_called_once_with(filters, skip, limit)


class TestPublishDocumentUseCase:
    """發布文檔用例測試"""
    
    def test_execute_document_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 創建一個模擬文檔
        mock_document = MagicMock(spec=Document)
        mock_repo.get_by_id.return_value = mock_document
        mock_repo.save.return_value = mock_document
        
        use_case = PublishDocumentUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id)
        
        # Assert
        assert result is not None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.publish.assert_called_once()
        mock_repo.save.assert_called_once_with(mock_document)
        mock_event_publisher.publish_all.assert_called_once()
    
    def test_execute_document_not_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 模擬文檔未找到
        mock_repo.get_by_id.return_value = None
        
        use_case = PublishDocumentUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id)
        
        # Assert
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_repo.save.assert_not_called()
        mock_event_publisher.publish_all.assert_not_called()


class TestDeleteDocumentUseCase:
    """刪除文檔用例測試"""
    
    def test_execute_success(self):
        # Arrange
        mock_repo = Mock()
        mock_repo.delete.return_value = True
        
        use_case = DeleteDocumentUseCase(mock_repo)
        document_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id)
        
        # Assert
        assert result is True
        mock_repo.delete.assert_called_once_with(document_id)
    
    def test_execute_failure(self):
        # Arrange
        mock_repo = Mock()
        mock_repo.delete.return_value = False
        
        use_case = DeleteDocumentUseCase(mock_repo)
        document_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id)
        
        # Assert
        assert result is False
        mock_repo.delete.assert_called_once_with(document_id)


class TestAddDocumentTagUseCase:
    """添加文檔標籤用例測試"""
    
    def test_execute_document_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 創建一個模擬文檔
        mock_document = MagicMock(spec=Document)
        mock_repo.get_by_id.return_value = mock_document
        mock_repo.save.return_value = mock_document
        
        use_case = AddDocumentTagUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        tag_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id, tag_id, user_id)
        
        # Assert
        assert result is not None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.add_tag.assert_called_once_with(tag_id)
        mock_repo.save.assert_called_once_with(mock_document)
        mock_event_publisher.publish.assert_called_once()
    
    def test_execute_document_not_found(self):
        # Arrange
        mock_repo = Mock()
        mock_event_publisher = Mock()
        
        # 模擬文檔未找到
        mock_repo.get_by_id.return_value = None
        
        use_case = AddDocumentTagUseCase(mock_repo, mock_event_publisher)
        document_id = uuid.uuid4()
        tag_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id, tag_id, user_id)
        
        # Assert
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_repo.save.assert_not_called()
        mock_event_publisher.publish.assert_not_called()