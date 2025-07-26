import pytest
import uuid
from datetime import datetime

from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.domain.events.document_events import DocumentCreated, DocumentUpdated, DocumentPublished


class TestDocument:
    """文檔實體測試"""
    
    def test_create_document(self):
        """測試創建文檔"""
        # Arrange
        title = "Test Document"
        content = "This is a test document"
        category_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        summary = "Test summary"
        tags = [uuid.uuid4(), uuid.uuid4()]
        
        # Act
        document = Document.create(
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id,
            summary=summary,
            tags=tags
        )
        
        # Assert
        assert document.title == title
        assert document.content == content
        assert document.category_id == category_id
        assert document.creator_id == creator_id
        assert document.summary == summary
        assert document.tags == tags
        assert document.status == DocumentStatus.DRAFT
        assert document.view_count == 0
        assert isinstance(document.id, uuid.UUID)
        assert isinstance(document.created_at, datetime)
        assert isinstance(document.updated_at, datetime)
        assert document.published_at is None
        
        # 檢查事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentCreated)
        assert events[0].document_id == document.id
        assert events[0].creator_id == creator_id
        assert events[0].title == title
        assert events[0].category_id == category_id
    
    def test_update_document(self):
        """測試更新文檔"""
        # Arrange
        document = Document.create(
            title="Original Title",
            content="Original Content",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        
        new_title = "Updated Title"
        new_content = "Updated Content"
        new_summary = "Updated Summary"
        new_category_id = uuid.uuid4()
        
        # 清空事件列表
        document.get_events()
        
        # Act
        document.update(
            title=new_title,
            content=new_content,
            summary=new_summary,
            category_id=new_category_id
        )
        
        # Assert
        assert document.title == new_title
        assert document.content == new_content
        assert document.summary == new_summary
        assert document.category_id == new_category_id
        
        # 檢查事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentUpdated)
        assert events[0].document_id == document.id
        assert events[0].updater_id == document.creator_id
        assert 'title' in events[0].changes
        assert 'content' in events[0].changes
        assert 'summary' in events[0].changes
        assert 'category_id' in events[0].changes
    
    def test_publish_document(self):
        """測試發布文檔"""
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        
        # 清空事件列表
        document.get_events()
        
        # Act
        document.publish()
        
        # Assert
        assert document.status == DocumentStatus.PUBLISHED
        assert document.published_at is not None
        
        # 檢查事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentPublished)
        assert events[0].document_id == document.id
        assert events[0].publisher_id == document.creator_id
    
    def test_unpublish_document(self):
        """測試取消發布文檔"""
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        document.publish()
        
        # 清空事件列表
        document.get_events()
        
        # Act
        document.unpublish()
        
        # Assert
        assert document.status == DocumentStatus.DRAFT
    
    def test_add_tag(self):
        """測試添加標籤"""
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        tag_id = uuid.uuid4()
        
        # Act
        document.add_tag(tag_id)
        
        # Assert
        assert tag_id in document.tags
    
    def test_remove_tag(self):
        """測試移除標籤"""
        # Arrange
        tag_id = uuid.uuid4()
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4(),
            tags=[tag_id]
        )
        
        # Act
        document.remove_tag(tag_id)
        
        # Assert
        assert tag_id not in document.tags
    
    def test_increment_view_count(self):
        """測試增加瀏覽次數"""
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        initial_view_count = document.view_count
        
        # Act
        document.increment_view_count()
        
        # Assert
        assert document.view_count == initial_view_count + 1