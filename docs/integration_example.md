# 乾淨架構、事件驅動設計與TDD整合示例

本文檔提供一個完整的示例，展示如何將乾淨架構、事件驅動設計和測試驅動開發（TDD）整合到知識庫系統中。我們將以文檔管理功能為例，展示從測試編寫到代碼實現的完整流程。

## 目錄

- [需求描述](#需求描述)
- [TDD 流程](#tdd-流程)
- [領域層實現](#領域層實現)
- [應用層實現](#應用層實現)
- [基礎設施層實現](#基礎設施層實現)
- [介面層實現](#介面層實現)
- [整合測試](#整合測試)
- [總結與反思](#總結與反思)

## 需求描述

我們需要實現一個文檔管理功能，包括以下需求：

1. 用戶可以創建新文檔，包括標題、內容、分類和標籤。
2. 用戶可以更新文檔的標題、內容、分類和標籤。
3. 用戶可以發布文檔，使其對其他用戶可見。
4. 用戶可以取消發布文檔，使其只對創建者可見。
5. 用戶可以查看文檔列表，包括按分類、創建者和標籤過濾。
6. 用戶可以搜索文檔，包括標題和內容。
7. 系統需要記錄文檔的瀏覽次數。
8. 系統需要記錄文檔的創建、更新、發布和瀏覽等事件。

## TDD 流程

我們將按照 TDD 的「紅-綠-重構」流程實現這個功能。

### 步驟 1：編寫文檔實體測試

首先，我們編寫文檔實體的測試：

```python
# tests/domain/entities/test_document.py
import pytest
import uuid
from datetime import datetime

# 這些導入會在實現代碼時創建
from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.domain.events.document_events import DocumentCreated, DocumentUpdated, DocumentPublished

class TestDocument:
    def test_create_document(self):
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
        assert document.created_at is not None
        assert document.updated_at is not None
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
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        document.get_events()  # 清除創建事件
        
        new_title = "Updated Document"
        new_content = "This is an updated document"
        updater_id = uuid.uuid4()
        
        # Act
        document.update(title=new_title, content=new_content, updater_id=updater_id)
        
        # Assert
        assert document.title == new_title
        assert document.content == new_content
        assert document.updated_at is not None
        
        # 檢查事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentUpdated)
        assert events[0].document_id == document.id
        assert events[0].updater_id == updater_id
        assert "title" in events[0].changes
        assert "content" in events[0].changes
    
    def test_publish_document(self):
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        document.get_events()  # 清除創建事件
        
        publisher_id = uuid.uuid4()
        
        # Act
        document.publish(publisher_id)
        
        # Assert
        assert document.status == DocumentStatus.PUBLISHED
        assert document.published_at is not None
        
        # 檢查事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentPublished)
        assert events[0].document_id == document.id
        assert events[0].publisher_id == publisher_id
    
    def test_unpublish_document(self):
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        document.publish(document.creator_id)
        document.get_events()  # 清除事件
        
        # Act
        document.unpublish()
        
        # Assert
        assert document.status == DocumentStatus.DRAFT
        assert document.published_at is not None  # 保留發布時間
    
    def test_add_tag(self):
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        document.get_events()  # 清除創建事件
        
        tag_id = uuid.uuid4()
        
        # Act
        document.add_tag(tag_id)
        
        # Assert
        assert tag_id in document.tags
    
    def test_remove_tag(self):
        # Arrange
        tag_id = uuid.uuid4()
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4(),
            tags=[tag_id]
        )
        document.get_events()  # 清除創建事件
        
        # Act
        document.remove_tag(tag_id)
        
        # Assert
        assert tag_id not in document.tags
    
    def test_increment_view_count(self):
        # Arrange
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        document.get_events()  # 清除創建事件
        initial_view_count = document.view_count
        
        # Act
        document.increment_view_count()
        
        # Assert
        assert document.view_count == initial_view_count + 1
```

運行測試，確認測試失敗（紅色）。

### 步驟 2：實現文檔實體

接下來，我們實現文檔實體：

```python
# src/domain/value_objects/document_status.py
from enum import Enum, auto

class DocumentStatus(Enum):
    DRAFT = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()
```

```python
# src/domain/events/base_event.py
from abc import ABC

class DomainEvent(ABC):
    """領域事件基類"""
    pass
```

```python
# src/domain/events/document_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List
import uuid

from .base_event import DomainEvent

@dataclass
class DocumentCreated(DomainEvent):
    document_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    category_id: uuid.UUID
    timestamp: datetime = datetime.now()

@dataclass
class DocumentUpdated(DomainEvent):
    document_id: uuid.UUID
    updater_id: uuid.UUID
    changes: Dict[str, Any]
    timestamp: datetime = datetime.now()

@dataclass
class DocumentPublished(DomainEvent):
    document_id: uuid.UUID
    publisher_id: uuid.UUID
    timestamp: datetime = datetime.now()

@dataclass
class DocumentViewed(DomainEvent):
    document_id: uuid.UUID
    viewer_id: uuid.UUID
    timestamp: datetime = datetime.now()

@dataclass
class DocumentTagAdded(DomainEvent):
    document_id: uuid.UUID
    tag_id: uuid.UUID
    timestamp: datetime = datetime.now()

@dataclass
class DocumentTagRemoved(DomainEvent):
    document_id: uuid.UUID
    tag_id: uuid.UUID
    timestamp: datetime = datetime.now()
```

```python
# src/domain/entities/document.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from ..value_objects.document_status import DocumentStatus
from ..events.document_events import (
    DocumentCreated, DocumentUpdated, DocumentPublished, 
    DocumentViewed, DocumentTagAdded, DocumentTagRemoved
)

@dataclass
class Document:
    id: uuid.UUID
    title: str
    content: str
    category_id: uuid.UUID
    creator_id: uuid.UUID
    status: DocumentStatus
    summary: Optional[str] = None
    view_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    tags: List[uuid.UUID] = field(default_factory=list)
    _events: List[Any] = field(default_factory=list, init=False)
    
    @classmethod
    def create(cls, title: str, content: str, category_id: uuid.UUID, 
               creator_id: uuid.UUID, summary: Optional[str] = None, 
               tags: List[uuid.UUID] = None) -> 'Document':
        """創建新文檔"""
        doc_id = uuid.uuid4()
        document = cls(
            id=doc_id,
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id,
            status=DocumentStatus.DRAFT,
            summary=summary,
            tags=tags or []
        )
        
        # 添加領域事件
        document._events.append(DocumentCreated(
            document_id=doc_id,
            creator_id=creator_id,
            title=title,
            category_id=category_id
        ))
        
        return document
    
    def update(self, updater_id: uuid.UUID, **kwargs) -> None:
        """更新文檔"""
        changes = {}
        
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                changes[key] = value
                setattr(self, key, value)
        
        if changes:
            self.updated_at = datetime.now()
            
            # 添加領域事件
            self._events.append(DocumentUpdated(
                document_id=self.id,
                updater_id=updater_id,
                changes=changes
            ))
    
    def publish(self, publisher_id: uuid.UUID) -> None:
        """發布文檔"""
        if self.status != DocumentStatus.PUBLISHED:
            self.status = DocumentStatus.PUBLISHED
            self.published_at = datetime.now()
            
            # 添加領域事件
            self._events.append(DocumentPublished(
                document_id=self.id,
                publisher_id=publisher_id
            ))
    
    def unpublish(self) -> None:
        """取消發布文檔"""
        if self.status == DocumentStatus.PUBLISHED:
            self.status = DocumentStatus.DRAFT
    
    def add_tag(self, tag_id: uuid.UUID) -> None:
        """添加標籤"""
        if tag_id not in self.tags:
            self.tags.append(tag_id)
            
            # 添加領域事件
            self._events.append(DocumentTagAdded(
                document_id=self.id,
                tag_id=tag_id
            ))
    
    def remove_tag(self, tag_id: uuid.UUID) -> None:
        """移除標籤"""
        if tag_id in self.tags:
            self.tags.remove(tag_id)
            
            # 添加領域事件
            self._events.append(DocumentTagRemoved(
                document_id=self.id,
                tag_id=tag_id
            ))
    
    def increment_view_count(self, viewer_id: uuid.UUID = None) -> None:
        """增加瀏覽次數"""
        self.view_count += 1
        
        # 添加領域事件
        if viewer_id:
            self._events.append(DocumentViewed(
                document_id=self.id,
                viewer_id=viewer_id
            ))
    
    def get_events(self) -> List[Any]:
        """獲取實體的領域事件"""
        events = self._events.copy()
        self._events.clear()
        return events
```

運行測試，確認測試通過（綠色）。

### 步驟 3：編寫儲存庫介面測試

接下來，我們編寫儲存庫介面的測試：

```python
# tests/domain/repositories/test_document_repository.py
import pytest
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

# 這些導入會在實現代碼時創建
from src.domain.repositories.document_repository import DocumentRepository
from src.domain.entities.document import Document

class TestDocumentRepository:
    def test_repository_interface(self):
        # 確認 DocumentRepository 是抽象類
        assert issubclass(DocumentRepository, ABC)
        
        # 確認 DocumentRepository 有必要的抽象方法
        assert hasattr(DocumentRepository, 'save')
        assert hasattr(DocumentRepository, 'get_by_id')
        assert hasattr(DocumentRepository, 'list')
        assert hasattr(DocumentRepository, 'delete')
        assert hasattr(DocumentRepository, 'get_by_category')
        assert hasattr(DocumentRepository, 'get_by_creator')
        assert hasattr(DocumentRepository, 'get_by_tag')
        assert hasattr(DocumentRepository, 'search')
```

運行測試，確認測試失敗（紅色）。

### 步驟 4：實現儲存庫介面

接下來，我們實現儲存庫介面：

```python
# src/domain/repositories/document_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from ..entities.document import Document
from ..value_objects.document_status import DocumentStatus

class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> Document:
        """保存文檔"""
        pass
    
    @abstractmethod
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """根據 ID 獲取文檔"""
        pass
    
    @abstractmethod
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        """列出文檔"""
        pass
    
    @abstractmethod
    def delete(self, document_id: uuid.UUID) -> bool:
        """刪除文檔"""
        pass
    
    @abstractmethod
    def get_by_category(self, category_id: uuid.UUID, status: DocumentStatus = None, 
                        skip: int = 0, limit: int = 100) -> List[Document]:
        """根據分類獲取文檔"""
        pass
    
    @abstractmethod
    def get_by_creator(self, creator_id: uuid.UUID, status: DocumentStatus = None, 
                       skip: int = 0, limit: int = 100) -> List[Document]:
        """根據創建者獲取文檔"""
        pass
    
    @abstractmethod
    def get_by_tag(self, tag_id: uuid.UUID, status: DocumentStatus = None, 
                   skip: int = 0, limit: int = 100) -> List[Document]:
        """根據標籤獲取文檔"""
        pass
    
    @abstractmethod
    def search(self, query: str, status: DocumentStatus = None, 
               skip: int = 0, limit: int = 100) -> List[Document]:
        """搜索文檔"""
        pass
```

運行測試，確認測試通過（綠色）。

### 步驟 5：編寫事件發布者介面測試

接下來，我們編寫事件發布者介面的測試：

```python
# tests/domain/events/test_event_publisher.py
import pytest
from abc import ABC, abstractmethod
from typing import List

# 這些導入會在實現代碼時創建
from src.domain.events.event_publisher import EventPublisher
from src.domain.events.base_event import DomainEvent

class TestEventPublisher:
    def test_event_publisher_interface(self):
        # 確認 EventPublisher 是抽象類
        assert issubclass(EventPublisher, ABC)
        
        # 確認 EventPublisher 有必要的抽象方法
        assert hasattr(EventPublisher, 'publish')
        assert hasattr(EventPublisher, 'publish_all')
```

運行測試，確認測試失敗（紅色）。

### 步驟 6：實現事件發布者介面

接下來，我們實現事件發布者介面：

```python
# src/domain/events/event_publisher.py
from abc import ABC, abstractmethod
from typing import List

from .base_event import DomainEvent

class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """發布事件"""
        pass
    
    @abstractmethod
    def publish_all(self, events: List[DomainEvent]) -> None:
        """發布多個事件"""
        pass
```

運行測試，確認測試通過（綠色）。

### 步驟 7：編寫用例測試

接下來，我們編寫用例的測試：

```python
# tests/application/use_cases/test_document_use_cases.py
import pytest
import uuid
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any

# 這些導入會在實現代碼時創建
from src.domain.entities.document import Document
from src.domain.repositories.document_repository import DocumentRepository
from src.domain.events.event_publisher import EventPublisher
from src.application.use_cases.document_use_cases import (
    CreateDocumentUseCase, GetDocumentUseCase, UpdateDocumentUseCase,
    ListDocumentsUseCase, PublishDocumentUseCase, DeleteDocumentUseCase,
    AddDocumentTagUseCase
)

class TestCreateDocumentUseCase:
    def test_execute(self):
        # Arrange
        mock_repo = Mock(spec=DocumentRepository)
        mock_repo.save.return_value = MagicMock(spec=Document)
        
        mock_publisher = Mock(spec=EventPublisher)
        
        use_case = CreateDocumentUseCase(mock_repo, mock_publisher)
        
        title = "Test Document"
        content = "This is a test document"
        category_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id
        )
        
        # Assert
        mock_repo.save.assert_called_once()
        mock_publisher.publish_all.assert_called_once()
        assert result is not None

class TestGetDocumentUseCase:
    def test_execute(self):
        # Arrange
        document_id = uuid.uuid4()
        mock_document = MagicMock(spec=Document)
        
        mock_repo = Mock(spec=DocumentRepository)
        mock_repo.get_by_id.return_value = mock_document
        
        mock_publisher = Mock(spec=EventPublisher)
        
        use_case = GetDocumentUseCase(mock_repo, mock_publisher)
        
        viewer_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id, viewer_id)
        
        # Assert
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.increment_view_count.assert_called_once_with(viewer_id)
        mock_repo.save.assert_called_once_with(mock_document)
        mock_publisher.publish_all.assert_called_once()
        assert result is mock_document

class TestUpdateDocumentUseCase:
    def test_execute(self):
        # Arrange
        document_id = uuid.uuid4()
        mock_document = MagicMock(spec=Document)
        
        mock_repo = Mock(spec=DocumentRepository)
        mock_repo.get_by_id.return_value = mock_document
        mock_repo.save.return_value = mock_document
        
        mock_publisher = Mock(spec=EventPublisher)
        
        use_case = UpdateDocumentUseCase(mock_repo, mock_publisher)
        
        updater_id = uuid.uuid4()
        updates = {"title": "Updated Title", "content": "Updated Content"}
        
        # Act
        result = use_case.execute(document_id, updater_id, **updates)
        
        # Assert
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.update.assert_called_once_with(updater_id=updater_id, **updates)
        mock_repo.save.assert_called_once_with(mock_document)
        mock_publisher.publish_all.assert_called_once()
        assert result is mock_document

class TestListDocumentsUseCase:
    def test_execute(self):
        # Arrange
        mock_documents = [MagicMock(spec=Document) for _ in range(3)]
        
        mock_repo = Mock(spec=DocumentRepository)
        mock_repo.list.return_value = mock_documents
        
        use_case = ListDocumentsUseCase(mock_repo)
        
        filters = {"status": "PUBLISHED"}
        skip = 0
        limit = 10
        
        # Act
        result = use_case.execute(filters, skip, limit)
        
        # Assert
        mock_repo.list.assert_called_once_with(filters, skip, limit)
        assert result == mock_documents

class TestPublishDocumentUseCase:
    def test_execute(self):
        # Arrange
        document_id = uuid.uuid4()
        mock_document = MagicMock(spec=Document)
        
        mock_repo = Mock(spec=DocumentRepository)
        mock_repo.get_by_id.return_value = mock_document
        mock_repo.save.return_value = mock_document
        
        mock_publisher = Mock(spec=EventPublisher)
        
        use_case = PublishDocumentUseCase(mock_repo, mock_publisher)
        
        publisher_id = uuid.uuid4()
        
        # Act
        result = use_case.execute(document_id, publisher_id)
        
        # Assert
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.publish.assert_called_once_with(publisher_id)
        mock_repo.save.assert_called_once_with(mock_document)
        mock_publisher.publish_all.assert_called_once()
        assert result is mock_document

class TestDeleteDocumentUseCase:
    def test_execute(self):
        # Arrange
        document_id = uuid.uuid4()
        
        mock_repo = Mock(spec=DocumentRepository)
        mock_repo.delete.return_value = True
        
        use_case = DeleteDocumentUseCase(mock_repo)
        
        # Act
        result = use_case.execute(document_id)
        
        # Assert
        mock_repo.delete.assert_called_once_with(document_id)
        assert result is True

class TestAddDocumentTagUseCase:
    def test_execute(self):
        # Arrange
        document_id = uuid.uuid4()
        tag_id = uuid.uuid4()
        mock_document = MagicMock(spec=Document)
        
        mock_repo = Mock(spec=DocumentRepository)
        mock_repo.get_by_id.return_value = mock_document
        mock_repo.save.return_value = mock_document
        
        mock_publisher = Mock(spec=EventPublisher)
        
        use_case = AddDocumentTagUseCase(mock_repo, mock_publisher)
        
        # Act
        result = use_case.execute(document_id, tag_id)
        
        # Assert
        mock_repo.get_by_id.assert_called_once_with(document_id)
        mock_document.add_tag.assert_called_once_with(tag_id)
        mock_repo.save.assert_called_once_with(mock_document)
        mock_publisher.publish_all.assert_called_once()
        assert result is mock_document
```

運行測試，確認測試失敗（紅色）。

### 步驟 8：實現用例

接下來，我們實現用例：

```python
# src/application/use_cases/document_use_cases.py
from typing import List, Optional, Dict, Any
import uuid

from ...domain.entities.document import Document
from ...domain.repositories.document_repository import DocumentRepository
from ...domain.events.event_publisher import EventPublisher
from ...domain.value_objects.document_status import DocumentStatus

class CreateDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, title: str, content: str, category_id: uuid.UUID, 
                creator_id: uuid.UUID, summary: Optional[str] = None, 
                tags: List[uuid.UUID] = None) -> Document:
        # 創建文檔實體
        document = Document.create(
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id,
            summary=summary,
            tags=tags
        )
        
        # 保存文檔
        saved_document = self.document_repository.save(document)
        
        # 發布事件
        events = document.get_events()
        self.event_publisher.publish_all(events)
        
        return saved_document

class GetDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, viewer_id: uuid.UUID = None) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        
        if document:
            # 增加瀏覽次數
            document.increment_view_count(viewer_id)
            
            # 保存文檔
            self.document_repository.save(document)
            
            # 發布事件
            events = document.get_events()
            self.event_publisher.publish_all(events)
        
        return document

class UpdateDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, updater_id: uuid.UUID, **kwargs) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        
        if document:
            # 更新文檔
            document.update(updater_id=updater_id, **kwargs)
            
            # 保存文檔
            saved_document = self.document_repository.save(document)
            
            # 發布事件
            events = document.get_events()
            self.event_publisher.publish_all(events)
            
            return saved_document
        
        return None

class ListDocumentsUseCase:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    def execute(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        # 列出文檔
        return self.document_repository.list(filters, skip, limit)

class PublishDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, publisher_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        
        if document:
            # 發布文檔
            document.publish(publisher_id)
            
            # 保存文檔
            saved_document = self.document_repository.save(document)
            
            # 發布事件
            events = document.get_events()
            self.event_publisher.publish_all(events)
            
            return saved_document
        
        return None

class UnpublishDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    def execute(self, document_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        
        if document:
            # 取消發布文檔
            document.unpublish()
            
            # 保存文檔
            saved_document = self.document_repository.save(document)
            
            return saved_document
        
        return None

class DeleteDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    def execute(self, document_id: uuid.UUID) -> bool:
        # 刪除文檔
        return self.document_repository.delete(document_id)

class AddDocumentTagUseCase:
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, tag_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        
        if document:
            # 添加標籤
            document.add_tag(tag_id)
            
            # 保存文檔
            saved_document = self.document_repository.save(document)
            
            # 發布事件
            events = document.get_events()
            self.event_publisher.publish_all(events)
            
            return saved_document
        
        return None

class RemoveDocumentTagUseCase:
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, tag_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        
        if document:
            # 移除標籤
            document.remove_tag(tag_id)
            
            # 保存文檔
            saved_document = self.document_repository.save(document)
            
            # 發布事件
            events = document.get_events()
            self.event_publisher.publish_all(events)
            
            return saved_document
        
        return None
```

運行測試，確認測試通過（綠色）。

### 步驟 9：編寫儲存庫實現測試

接下來，我們編寫儲存庫實現的測試：

```python
# tests/infrastructure/repositories/test_document_repository_impl.py
import pytest
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 這些導入會在實現代碼時創建
from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.infrastructure.repositories.document_repository_impl import SQLAlchemyDocumentRepository
from src.infrastructure.database.models import DocumentModel, TagModel, Base

@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()

class TestSQLAlchemyDocumentRepository:
    def test_save_new_document(self, db_session):
        # Arrange
        repo = SQLAlchemyDocumentRepository(db_session)
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        
        # Act
        saved_document = repo.save(document)
        
        # Assert
        assert saved_document.id == document.id
        assert saved_document.title == document.title
        assert saved_document.content == document.content
        
        # 檢查資料庫
        db_document = db_session.query(DocumentModel).filter_by(id=str(document.id)).first()
        assert db_document is not None
        assert db_document.title == document.title
    
    def test_get_by_id(self, db_session):
        # Arrange
        repo = SQLAlchemyDocumentRepository(db_session)
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        repo.save(document)
        
        # Act
        retrieved_document = repo.get_by_id(document.id)
        
        # Assert
        assert retrieved_document is not None
        assert retrieved_document.id == document.id
        assert retrieved_document.title == document.title
    
    def test_list(self, db_session):
        # Arrange
        repo = SQLAlchemyDocumentRepository(db_session)
        for i in range(3):
            document = Document.create(
                title=f"Test Document {i}",
                content=f"This is test document {i}",
                category_id=uuid.uuid4(),
                creator_id=uuid.uuid4()
            )
            repo.save(document)
        
        # Act
        documents = repo.list()
        
        # Assert
        assert len(documents) == 3
    
    def test_delete(self, db_session):
        # Arrange
        repo = SQLAlchemyDocumentRepository(db_session)
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        repo.save(document)
        
        # Act
        result = repo.delete(document.id)
        
        # Assert
        assert result is True
        assert repo.get_by_id(document.id) is None
```

運行測試，確認測試失敗（紅色）。

### 步驟 10：實現儲存庫

接下來，我們實現儲存庫：

```python
# src/infrastructure/database/models.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Table, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# 文檔標籤關聯表
document_tags = Table(
    'document_tags',
    Base.metadata,
    Column('document_id', String, ForeignKey('documents.id')),
    Column('tag_id', String, ForeignKey('tags.id'))
)

class DocumentModel(Base):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category_id = Column(String, nullable=False)
    creator_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    tags = relationship('TagModel', secondary=document_tags, backref='documents')

class TagModel(Base):
    __tablename__ = 'tags'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
```

```python
# src/infrastructure/repositories/document_repository_impl.py
from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ...domain.entities.document import Document
from ...domain.repositories.document_repository import DocumentRepository
from ...domain.value_objects.document_status import DocumentStatus
from ..database.models import DocumentModel, TagModel

class SQLAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, document: Document) -> Document:
        # 檢查文檔是否已存在
        db_document = self.session.query(DocumentModel).filter_by(id=str(document.id)).first()
        
        if db_document is None:
            # 創建新文檔
            db_document = DocumentModel(
                id=str(document.id),
                title=document.title,
                content=document.content,
                category_id=str(document.category_id),
                creator_id=str(document.creator_id),
                status=document.status.name,
                summary=document.summary,
                view_count=document.view_count,
                created_at=document.created_at,
                updated_at=document.updated_at,
                published_at=document.published_at
            )
            self.session.add(db_document)
        else:
            # 更新現有文檔
            db_document.title = document.title
            db_document.content = document.content
            db_document.category_id = str(document.category_id)
            db_document.status = document.status.name
            db_document.summary = document.summary
            db_document.view_count = document.view_count
            db_document.updated_at = document.updated_at
            db_document.published_at = document.published_at
        
        # 更新標籤
        db_document.tags = []
        for tag_id in document.tags:
            tag = self.session.query(TagModel).filter_by(id=str(tag_id)).first()
            if tag:
                db_document.tags.append(tag)
        
        self.session.commit()
        
        return self._to_entity(db_document)
    
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        db_document = self.session.query(DocumentModel).filter_by(id=str(document_id)).first()
        
        if db_document:
            return self._to_entity(db_document)
        
        return None
    
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        query = self.session.query(DocumentModel)
        
        if filters:
            if 'category_id' in filters:
                query = query.filter(DocumentModel.category_id == str(filters['category_id']))
            
            if 'creator_id' in filters:
                query = query.filter(DocumentModel.creator_id == str(filters['creator_id']))
            
            if 'status' in filters:
                query = query.filter(DocumentModel.status == filters['status'])
        
        db_documents = query.offset(skip).limit(limit).all()
        
        return [self._to_entity(db_document) for db_document in db_documents]
    
    def delete(self, document_id: uuid.UUID) -> bool:
        db_document = self.session.query(DocumentModel).filter_by(id=str(document_id)).first()
        
        if db_document:
            # 刪除文檔標籤關聯
            db_document.tags = []
            
            # 刪除文檔
            self.session.delete(db_document)
            self.session.commit()
            return True
        
        return False
    
    def get_by_category(self, category_id: uuid.UUID, status: DocumentStatus = None, 
                        skip: int = 0, limit: int = 100) -> List[Document]:
        query = self.session.query(DocumentModel).filter(DocumentModel.category_id == str(category_id))
        
        if status:
            query = query.filter(DocumentModel.status == status.name)
        
        db_documents = query.offset(skip).limit(limit).all()
        
        return [self._to_entity(db_document) for db_document in db_documents]
    
    def get_by_creator(self, creator_id: uuid.UUID, status: DocumentStatus = None, 
                       skip: int = 0, limit: int = 100) -> List[Document]:
        query = self.session.query(DocumentModel).filter(DocumentModel.creator_id == str(creator_id))
        
        if status:
            query = query.filter(DocumentModel.status == status.name)
        
        db_documents = query.offset(skip).limit(limit).all()
        
        return [self._to_entity(db_document) for db_document in db_documents]
    
    def get_by_tag(self, tag_id: uuid.UUID, status: DocumentStatus = None, 
                   skip: int = 0, limit: int = 100) -> List[Document]:
        query = self.session.query(DocumentModel).join(DocumentModel.tags).filter(TagModel.id == str(tag_id))
        
        if status:
            query = query.filter(DocumentModel.status == status.name)
        
        db_documents = query.offset(skip).limit(limit).all()
        
        return [self._to_entity(db_document) for db_document in db_documents]
    
    def search(self, query: str, status: DocumentStatus = None, 
               skip: int = 0, limit: int = 100) -> List[Document]:
        db_query = self.session.query(DocumentModel).filter(
            or_(
                DocumentModel.title.ilike(f'%{query}%'),
                DocumentModel.content.ilike(f'%{query}%')
            )
        )
        
        if status:
            db_query = db_query.filter(DocumentModel.status == status.name)
        
        db_documents = db_query.offset(skip).limit(limit).all()
        
        return [self._to_entity(db_document) for db_document in db_documents]
    
    def _to_entity(self, db_document: DocumentModel) -> Document:
        """將資料庫模型轉換為領域實體"""
        return Document(
            id=uuid.UUID(db_document.id),
            title=db_document.title,
            content=db_document.content,
            category_id=uuid.UUID(db_document.category_id),
            creator_id=uuid.UUID(db_document.creator_id),
            status=DocumentStatus[db_document.status],
            summary=db_document.summary,
            view_count=db_document.view_count,
            created_at=db_document.created_at,
            updated_at=db_document.updated_at,
            published_at=db_document.published_at,
            tags=[uuid.UUID(tag.id) for tag in db_document.tags]
        )
```

### 步驟 11：編寫事件發布者實現測試

接下來，我們編寫事件發布者實現的測試：

```python
# tests/infrastructure/events/test_event_publisher_impl.py
import pytest
from unittest.mock import Mock

# 這些導入會在實現代碼時創建
from src.domain.events.base_event import DomainEvent
from src.domain.events.document_events import DocumentCreated
from src.infrastructure.events.event_publisher_impl import InMemoryEventPublisher

class TestInMemoryEventPublisher:
    def test_publish(self):
        # Arrange
        publisher = InMemoryEventPublisher()
        mock_handler = Mock()
        event = DocumentCreated(
            document_id=Mock(),
            creator_id=Mock(),
            title="Test Document",
            category_id=Mock()
        )
        
        # 註冊處理器
        publisher.register_handler(DocumentCreated, mock_handler)
        
        # Act
        publisher.publish(event)
        
        # Assert
        mock_handler.assert_called_once_with(event)
    
    def test_publish_all(self):
        # Arrange
        publisher = InMemoryEventPublisher()
        mock_handler = Mock()
        events = [
            DocumentCreated(
                document_id=Mock(),
                creator_id=Mock(),
                title="Test Document 1",
                category_id=Mock()
            ),
            DocumentCreated(
                document_id=Mock(),
                creator_id=Mock(),
                title="Test Document 2",
                category_id=Mock()
            )
        ]
        
        # 註冊處理器
        publisher.register_handler(DocumentCreated, mock_handler)
        
        # Act
        publisher.publish_all(events)
        
        # Assert
        assert mock_handler.call_count == 2
```

運行測試，確認測試失敗（紅色）。

### 步驟 12：實現事件發布者

接下來，我們實現事件發布者：

```python
# src/infrastructure/events/event_publisher_impl.py
from typing import List, Dict, Type, Callable, Any
import logging
import json
import uuid
from datetime import datetime

from ...domain.events.base_event import DomainEvent
from ...domain.events.event_publisher import EventPublisher

class InMemoryEventPublisher(EventPublisher):
    def __init__(self):
        self.handlers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_handler(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """註冊事件處理器"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent) -> None:
        """發布事件"""
        event_type = type(event)
        self.logger.info(f"Publishing event: {event_type.__name__}")
        
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error handling event {event_type.__name__}: {str(e)}")
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """發布多個事件"""
        for event in events:
            self.publish(event)

class AsyncEventPublisher(EventPublisher):
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.logger = logging.getLogger(__name__)
    
    def publish(self, event: DomainEvent) -> None:
        """發布事件到消息隊列"""
        event_type = type(event).__name__
        self.logger.info(f"Publishing event to queue: {event_type}")
        
        # 序列化事件
        event_data = self._serialize_event(event)
        
        # 發布到消息隊列
        # 這裡可以使用 RabbitMQ、Kafka 等消息隊列
        # 例如：self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=event_data)
        
        self.logger.info(f"Event published: {event_type}")
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """發布多個事件到消息隊列"""
        for event in events:
            self.publish(event)
    
    def _serialize_event(self, event: DomainEvent) -> str:
        """序列化事件"""
        event_dict = self._event_to_dict(event)
        return json.dumps(event_dict)
    
    def _event_to_dict(self, event: DomainEvent) -> Dict[str, Any]:
        """將事件轉換為字典"""
        event_dict = {
            'event_type': type(event).__name__,
            'timestamp': datetime.now().isoformat()
        }
        
        # 添加事件屬性
        for key, value in event.__dict__.items():
            if isinstance(value, uuid.UUID):
                event_dict[key] = str(value)
            elif isinstance(value, datetime):
                event_dict[key] = value.isoformat()
            else:
                event_dict[key] = value
        
        return event_dict

# 事件處理器示例
def document_created_handler(event: DomainEvent) -> None:
    """處理文檔創建事件"""
    logger = logging.getLogger(__name__)
    logger.info(f"Document created: {event.document_id} by {event.creator_id}")
    # 這裡可以添加更多邏輯，如發送通知、更新索引等

def document_updated_handler(event: DomainEvent) -> None:
    """處理文檔更新事件"""
    logger = logging.getLogger(__name__)
    logger.info(f"Document updated: {event.document_id} by {event.updater_id}")
    # 這裡可以添加更多邏輯，如發送通知、更新索引等

def document_published_handler(event: DomainEvent) -> None:
    """處理文檔發布事件"""
    logger = logging.getLogger(__name__)
    logger.info(f"Document published: {event.document_id} by {event.publisher_id}")
    # 這裡可以添加更多邏輯，如發送通知、更新索引等

def document_viewed_handler(event: DomainEvent) -> None:
    """處理文檔瀏覽事件"""
    logger = logging.getLogger(__name__)
    logger.info(f"Document viewed: {event.document_id} by {event.viewer_id}")
    # 這裡可以添加更多邏輯，如更新熱門文檔等
```

運行測試，確認測試通過（綠色）。

### 步驟 13：編寫 API 控制器測試

接下來，我們編寫 API 控制器的測試：

```python
# tests/interface/api/test_document_controller.py
import pytest
import uuid
from unittest.mock import Mock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

# 這些導入會在實現代碼時創建
from src.domain.entities.document import Document
from src.application.use_cases.document_use_cases import CreateDocumentUseCase
from src.interface.api.document_controller import router

app = FastAPI()
app.include_router(router, prefix="/documents")

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_create_document_use_case(monkeypatch):
    mock_use_case = Mock(spec=CreateDocumentUseCase)
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid.uuid4()
    mock_document.title = "Test Document"
    mock_document.content = "This is a test document"
    mock_use_case.execute.return_value = mock_document
    
    # 替換依賴
    monkeypatch.setattr("src.interface.api.document_controller.get_create_document_use_case", lambda: mock_use_case)
    
    return mock_use_case

class TestDocumentController:
    def test_create_document(self, client, mock_create_document_use_case):
        # Arrange
        data = {
            "title": "Test Document",
            "content": "This is a test document",
            "category_id": str(uuid.uuid4()),
            "creator_id": str(uuid.uuid4())
        }
        
        # Act
        response = client.post("/documents/", json=data)
        
        # Assert
        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["title"] == data["title"]
        mock_create_document_use_case.execute.assert_called_once()
```

運行測試，確認測試失敗（紅色）。

### 步驟 14：實現 API 控制器

接下來，我們實現 API 控制器：

```python
# src/interface/api/document_controller.py
from typing import List, Optional, Dict, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...domain.entities.document import Document
from ...domain.value_objects.document_status import DocumentStatus
from ...application.use_cases.document_use_cases import (
    CreateDocumentUseCase, GetDocumentUseCase, UpdateDocumentUseCase,
    ListDocumentsUseCase, PublishDocumentUseCase, UnpublishDocumentUseCase,
    DeleteDocumentUseCase, AddDocumentTagUseCase, RemoveDocumentTagUseCase
)
from ...infrastructure.repositories.document_repository_impl import SQLAlchemyDocumentRepository
from ...infrastructure.events.event_publisher_impl import InMemoryEventPublisher

router = APIRouter()

# 依賴注入
def get_document_repository():
    # 這裡應該從依賴注入容器獲取會話
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from ...infrastructure.database.models import Base
    
    engine = create_engine("sqlite:///./knowledge.db")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield SQLAlchemyDocumentRepository(session)
    finally:
        session.close()

def get_event_publisher():
    publisher = InMemoryEventPublisher()
    # 註冊事件處理器
    from ...infrastructure.events.event_publisher_impl import (
        document_created_handler, document_updated_handler,
        document_published_handler, document_viewed_handler
    )
    from ...domain.events.document_events import (
        DocumentCreated, DocumentUpdated, DocumentPublished, DocumentViewed
    )
    
    publisher.register_handler(DocumentCreated, document_created_handler)
    publisher.register_handler(DocumentUpdated, document_updated_handler)
    publisher.register_handler(DocumentPublished, document_published_handler)
    publisher.register_handler(DocumentViewed, document_viewed_handler)
    
    return publisher

# 用例工廠
def get_create_document_use_case():
    return CreateDocumentUseCase(
        document_repository=get_document_repository(),
        event_publisher=get_event_publisher()
    )

def get_get_document_use_case():
    return GetDocumentUseCase(
        document_repository=get_document_repository(),
        event_publisher=get_event_publisher()
    )

def get_update_document_use_case():
    return UpdateDocumentUseCase(
        document_repository=get_document_repository(),
        event_publisher=get_event_publisher()
    )

def get_list_documents_use_case():
    return ListDocumentsUseCase(
        document_repository=get_document_repository()
    )

def get_publish_document_use_case():
    return PublishDocumentUseCase(
        document_repository=get_document_repository(),
        event_publisher=get_event_publisher()
    )

def get_unpublish_document_use_case():
    return UnpublishDocumentUseCase(
        document_repository=get_document_repository()
    )

def get_delete_document_use_case():
    return DeleteDocumentUseCase(
        document_repository=get_document_repository()
    )

def get_add_document_tag_use_case():
    return AddDocumentTagUseCase(
        document_repository=get_document_repository(),
        event_publisher=get_event_publisher()
    )

def get_remove_document_tag_use_case():
    return RemoveDocumentTagUseCase(
        document_repository=get_document_repository(),
        event_publisher=get_event_publisher()
    )

# 請求模型
class CreateDocumentRequest(BaseModel):
    title: str
    content: str
    category_id: str
    creator_id: str
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None
    summary: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    category_id: str
    creator_id: str
    status: str
    summary: Optional[str] = None
    view_count: int
    created_at: str
    updated_at: str
    published_at: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

# 路由
@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    request: CreateDocumentRequest,
    use_case: CreateDocumentUseCase = Depends(get_create_document_use_case)
):
    """創建文檔"""
    document = use_case.execute(
        title=request.title,
        content=request.content,
        category_id=uuid.UUID(request.category_id),
        creator_id=uuid.UUID(request.creator_id),
        summary=request.summary,
        tags=[uuid.UUID(tag) for tag in request.tags] if request.tags else None
    )
    
    return _document_to_response(document)

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    viewer_id: Optional[str] = None,
    use_case: GetDocumentUseCase = Depends(get_get_document_use_case)
):
    """獲取文檔"""
    document = use_case.execute(
        document_id=uuid.UUID(document_id),
        viewer_id=uuid.UUID(viewer_id) if viewer_id else None
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return _document_to_response(document)

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    updater_id: str,
    use_case: UpdateDocumentUseCase = Depends(get_update_document_use_case)
):
    """更新文檔"""
    updates = {k: v for k, v in request.dict().items() if v is not None}
    
    if "category_id" in updates:
        updates["category_id"] = uuid.UUID(updates["category_id"])
    
    document = use_case.execute(
        document_id=uuid.UUID(document_id),
        updater_id=uuid.UUID(updater_id),
        **updates
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return _document_to_response(document)

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    category_id: Optional[str] = None,
    creator_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    use_case: ListDocumentsUseCase = Depends(get_list_documents_use_case)
):
    """列出文檔"""
    filters = {}
    
    if category_id:
        filters["category_id"] = uuid.UUID(category_id)
    
    if creator_id:
        filters["creator_id"] = uuid.UUID(creator_id)
    
    if status:
        filters["status"] = status
    
    documents = use_case.execute(filters, skip, limit)
    
    return [_document_to_response(document) for document in documents]

@router.post("/{document_id}/publish", response_model=DocumentResponse)
def publish_document(
    document_id: str,
    publisher_id: str,
    use_case: PublishDocumentUseCase = Depends(get_publish_document_use_case)
):
    """發布文檔"""
    document = use_case.execute(
        document_id=uuid.UUID(document_id),
        publisher_id=uuid.UUID(publisher_id)
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return _document_to_response(document)

@router.post("/{document_id}/unpublish", response_model=DocumentResponse)
def unpublish_document(
    document_id: str,
    use_case: UnpublishDocumentUseCase = Depends(get_unpublish_document_use_case)
):
    """取消發布文檔"""
    document = use_case.execute(document_id=uuid.UUID(document_id))
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return _document_to_response(document)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    use_case: DeleteDocumentUseCase = Depends(get_delete_document_use_case)
):
    """刪除文檔"""
    result = use_case.execute(document_id=uuid.UUID(document_id))
    
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")

@router.post("/{document_id}/tags/{tag_id}", response_model=DocumentResponse)
def add_document_tag(
    document_id: str,
    tag_id: str,
    use_case: AddDocumentTagUseCase = Depends(get_add_document_tag_use_case)
):
    """添加文檔標籤"""
    document = use_case.execute(
        document_id=uuid.UUID(document_id),
        tag_id=uuid.UUID(tag_id)
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return _document_to_response(document)

@router.delete("/{document_id}/tags/{tag_id}", response_model=DocumentResponse)
def remove_document_tag(
    document_id: str,
    tag_id: str,
    use_case: RemoveDocumentTagUseCase = Depends(get_remove_document_tag_use_case)
):
    """移除文檔標籤"""
    document = use_case.execute(
        document_id=uuid.UUID(document_id),
        tag_id=uuid.UUID(tag_id)
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return _document_to_response(document)

def _document_to_response(document: Document) -> Dict[str, Any]:
    """將文檔實體轉換為響應模型"""
    return {
        "id": str(document.id),
        "title": document.title,
        "content": document.content,
        "category_id": str(document.category_id),
        "creator_id": str(document.creator_id),
        "status": document.status.name,
        "summary": document.summary,
        "view_count": document.view_count,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
        "published_at": document.published_at.isoformat() if document.published_at else None,
        "tags": [str(tag) for tag in document.tags]
    }