# 乾淨架構與事件驅動設計實現方案

## 1. 乾淨架構概述

乾淨架構（Clean Architecture）是一種軟體設計理念，旨在創建一個獨立於框架、UI、數據庫和外部依賴的系統。它通過分層和依賴規則，使系統更易於測試、維護和擴展。

### 核心原則

1. **依賴規則**：依賴關係只能從外層指向內層，內層不應該知道外層的存在
2. **關注點分離**：每一層都有其特定的職責
3. **業務邏輯獨立**：核心業務邏輯不依賴於外部框架和工具

### 架構層次

![乾淨架構圖](https://blog.cleancoder.com/uncle-bob/images/2012-08-13-the-clean-architecture/CleanArchitecture.jpg)

1. **實體層（Entities）**：包含業務規則和數據結構
2. **用例層（Use Cases）**：包含應用特定的業務規則
3. **介面適配層（Interface Adapters）**：將用例和實體數據轉換為外部格式
4. **框架與驅動層（Frameworks & Drivers）**：包含所有外部細節，如數據庫、Web框架等

## 2. 事件驅動設計整合

事件驅動設計（Event-Driven Design）是一種設計模式，系統中的組件通過事件進行通信，而不是直接調用。這種方式可以降低組件間的耦合度，提高系統的可擴展性和靈活性。

### 核心概念

1. **領域事件（Domain Events）**：代表系統中發生的重要業務事件
2. **事件發布/訂閱**：組件可以發布事件或訂閱感興趣的事件
3. **事件處理器**：負責處理特定類型的事件

### 與乾淨架構的整合

- 領域事件定義在實體層或用例層
- 事件發布機制可以作為用例層的一部分
- 事件處理器可以位於不同的層次，根據其職責

## 3. TDD 開發流程

測試驅動開發（Test-Driven Development, TDD）是一種開發方法，開發者先編寫測試，然後編寫代碼使測試通過，最後重構代碼。

### TDD 循環

1. **紅**：編寫一個失敗的測試
2. **綠**：編寫最少量的代碼使測試通過
3. **重構**：改進代碼，保持測試通過

### 在乾淨架構中應用 TDD

- 從內層（實體和用例）開始測試
- 使用模擬（Mock）隔離外部依賴
- 為每一層編寫單元測試和集成測試

## 4. 知識庫系統的乾淨架構實現

### 4.1 目錄結構

```
src/
  domain/                 # 領域層（實體層）
    entities/             # 領域實體
    events/               # 領域事件
    repositories/         # 儲存庫介面
    value_objects/        # 值物件
    exceptions/           # 領域異常
  
  application/            # 應用層（用例層）
    use_cases/            # 用例
    services/             # 應用服務
    dtos/                 # 數據傳輸物件
    interfaces/           # 應用層介面
    events/               # 應用層事件處理
  
  infrastructure/         # 基礎設施層
    persistence/          # 持久化實現
      sqlalchemy/         # SQLAlchemy 實現
      elasticsearch/      # Elasticsearch 實現
    messaging/            # 消息傳遞實現
    security/             # 安全相關實現
    logging/              # 日誌實現
  
  interfaces/             # 介面層
    api/                  # API 介面
      rest/               # REST API
      graphql/            # GraphQL API
    events/               # 事件處理器
```

### 4.2 領域層（Domain Layer）

#### 實體（Entities）

```python
# domain/entities/document.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from ..value_objects.document_status import DocumentStatus
from ..events.document_events import DocumentCreated, DocumentUpdated, DocumentPublished


@dataclass
class Document:
    """文檔實體"""
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
    
    def update(self, title: Optional[str] = None, content: Optional[str] = None,
               summary: Optional[str] = None, category_id: Optional[uuid.UUID] = None) -> None:
        """更新文檔"""
        changes = {}
        
        if title is not None and title != self.title:
            changes['title'] = {'old': self.title, 'new': title}
            self.title = title
            
        if content is not None and content != self.content:
            changes['content'] = {'old': '...', 'new': '...'}
            self.content = content
            
        if summary is not None and summary != self.summary:
            changes['summary'] = {'old': self.summary, 'new': summary}
            self.summary = summary
            
        if category_id is not None and category_id != self.category_id:
            changes['category_id'] = {'old': str(self.category_id), 'new': str(category_id)}
            self.category_id = category_id
        
        if changes:
            self.updated_at = datetime.now()
            
            # 添加領域事件
            self._events.append(DocumentUpdated(
                document_id=self.id,
                updater_id=self.creator_id,  # 假設更新者是創建者
                changes=changes
            ))
    
    def publish(self) -> None:
        """發布文檔"""
        if self.status != DocumentStatus.PUBLISHED:
            self.status = DocumentStatus.PUBLISHED
            self.published_at = datetime.now()
            self.updated_at = datetime.now()
            
            # 添加領域事件
            self._events.append(DocumentPublished(
                document_id=self.id,
                publisher_id=self.creator_id
            ))
    
    def unpublish(self) -> None:
        """取消發布文檔"""
        if self.status == DocumentStatus.PUBLISHED:
            self.status = DocumentStatus.DRAFT
            self.updated_at = datetime.now()
    
    def add_tag(self, tag_id: uuid.UUID) -> None:
        """添加標籤"""
        if tag_id not in self.tags:
            self.tags.append(tag_id)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag_id: uuid.UUID) -> None:
        """移除標籤"""
        if tag_id in self.tags:
            self.tags.remove(tag_id)
            self.updated_at = datetime.now()
    
    def increment_view_count(self) -> None:
        """增加瀏覽次數"""
        self.view_count += 1
    
    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events
```

#### 值物件（Value Objects）

```python
# domain/value_objects/document_status.py
from enum import Enum, auto


class DocumentStatus(Enum):
    """文檔狀態"""
    DRAFT = auto()       # 草稿
    PUBLISHED = auto()   # 已發布
    ARCHIVED = auto()    # 已歸檔
```

#### 領域事件（Domain Events）

```python
# domain/events/document_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from .base_event import DomainEvent


@dataclass
class DocumentCreated(DomainEvent):
    """文檔創建事件"""
    document_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    category_id: uuid.UUID
    timestamp: datetime = datetime.now()


@dataclass
class DocumentUpdated(DomainEvent):
    """文檔更新事件"""
    document_id: uuid.UUID
    updater_id: uuid.UUID
    changes: Dict[str, Any]
    timestamp: datetime = datetime.now()


@dataclass
class DocumentPublished(DomainEvent):
    """文檔發布事件"""
    document_id: uuid.UUID
    publisher_id: uuid.UUID
    timestamp: datetime = datetime.now()


@dataclass
class DocumentViewed(DomainEvent):
    """文檔瀏覽事件"""
    document_id: uuid.UUID
    viewer_id: Optional[uuid.UUID]
    timestamp: datetime = datetime.now()
```

```python
# domain/events/base_event.py
from abc import ABC


class DomainEvent(ABC):
    """領域事件基類"""
    pass
```

#### 儲存庫介面（Repository Interfaces）

```python
# domain/repositories/document_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from ..entities.document import Document


class DocumentRepository(ABC):
    """文檔儲存庫介面"""
    
    @abstractmethod
    def save(self, document: Document) -> Document:
        """保存文檔"""
        pass
    
    @abstractmethod
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """根據ID獲取文檔"""
        pass
    
    @abstractmethod
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        """獲取文檔列表"""
        pass
    
    @abstractmethod
    def delete(self, document_id: uuid.UUID) -> bool:
        """刪除文檔"""
        pass
```

### 4.3 應用層（Application Layer）

#### 用例（Use Cases）

```python
# application/use_cases/document/create_document.py
from dataclasses import dataclass
from typing import List, Optional
import uuid

from ....domain.entities.document import Document
from ....domain.repositories.document_repository import DocumentRepository
from ....domain.repositories.category_repository import CategoryRepository
from ....domain.exceptions.not_found_exception import NotFoundException
from ...interfaces.event_publisher import EventPublisher


@dataclass
class CreateDocumentCommand:
    """創建文檔命令"""
    title: str
    content: str
    category_id: uuid.UUID
    creator_id: uuid.UUID
    summary: Optional[str] = None
    tag_ids: List[uuid.UUID] = None
    is_published: bool = False


class CreateDocumentUseCase:
    """創建文檔用例"""
    
    def __init__(self, document_repository: DocumentRepository, 
                 category_repository: CategoryRepository,
                 event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.category_repository = category_repository
        self.event_publisher = event_publisher
    
    def execute(self, command: CreateDocumentCommand) -> Document:
        """執行用例"""
        # 檢查分類是否存在
        category = self.category_repository.get_by_id(command.category_id)
        if not category:
            raise NotFoundException(f"分類 {command.category_id} 不存在")
        
        # 創建文檔實體
        document = Document.create(
            title=command.title,
            content=command.content,
            category_id=command.category_id,
            creator_id=command.creator_id,
            summary=command.summary,
            tags=command.tag_ids or []
        )
        
        # 如果需要發布
        if command.is_published:
            document.publish()
        
        # 保存文檔
        saved_document = self.document_repository.save(document)
        
        # 發布領域事件
        for event in document.get_events():
            self.event_publisher.publish(event)
        
        return saved_document
```

#### 應用層介面（Application Interfaces）

```python
# application/interfaces/event_publisher.py
from abc import ABC, abstractmethod
from typing import Any


class EventPublisher(ABC):
    """事件發布者介面"""
    
    @abstractmethod
    def publish(self, event: Any) -> None:
        """發布事件"""
        pass
```

### 4.4 基礎設施層（Infrastructure Layer）

#### 儲存庫實現（Repository Implementation）

```python
# infrastructure/persistence/sqlalchemy/document_repository.py
from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from ....domain.entities.document import Document
from ....domain.repositories.document_repository import DocumentRepository
from ....domain.value_objects.document_status import DocumentStatus
from ..models.document import DocumentModel
from ..models.document_tag import document_tag_association


class SQLAlchemyDocumentRepository(DocumentRepository):
    """SQLAlchemy 文檔儲存庫實現"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, document: Document) -> Document:
        """保存文檔"""
        # 檢查是否存在
        db_document = self.session.query(DocumentModel).filter(DocumentModel.id == document.id).first()
        
        if not db_document:
            # 創建新記錄
            db_document = DocumentModel(
                id=document.id,
                title=document.title,
                content=document.content,
                summary=document.summary,
                category_id=document.category_id,
                creator_id=document.creator_id,
                is_published=(document.status == DocumentStatus.PUBLISHED),
                view_count=document.view_count,
                created_at=document.created_at,
                updated_at=document.updated_at,
                published_at=document.published_at
            )
            self.session.add(db_document)
        else:
            # 更新現有記錄
            db_document.title = document.title
            db_document.content = document.content
            db_document.summary = document.summary
            db_document.category_id = document.category_id
            db_document.is_published = (document.status == DocumentStatus.PUBLISHED)
            db_document.view_count = document.view_count
            db_document.updated_at = document.updated_at
            db_document.published_at = document.published_at
        
        # 處理標籤關聯
        if document.tags:
            # 清除現有標籤
            self.session.query(document_tag_association).filter(
                document_tag_association.c.document_id == document.id
            ).delete()
            
            # 添加新標籤
            for tag_id in document.tags:
                self.session.execute(
                    document_tag_association.insert().values(
                        document_id=document.id,
                        tag_id=tag_id
                    )
                )
        
        self.session.commit()
        
        # 重新加載以獲取完整數據
        self.session.refresh(db_document)
        
        # 轉換為領域實體
        return self._to_entity(db_document)
    
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """根據ID獲取文檔"""
        db_document = self.session.query(DocumentModel).options(
            joinedload(DocumentModel.category),
            joinedload(DocumentModel.creator),
            joinedload(DocumentModel.tags)
        ).filter(DocumentModel.id == document_id).first()
        
        if not db_document:
            return None
        
        return self._to_entity(db_document)
    
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        """獲取文檔列表"""
        query = self.session.query(DocumentModel)
        
        # 應用篩選條件
        if filters:
            if filters.get("category_id"):
                query = query.filter(DocumentModel.category_id == filters["category_id"])
            if filters.get("creator_id"):
                query = query.filter(DocumentModel.creator_id == filters["creator_id"])
            if filters.get("is_published") is not None:
                query = query.filter(DocumentModel.is_published == filters["is_published"])
            if filters.get("tag_id"):
                query = query.join(document_tag_association).filter(
                    document_tag_association.c.tag_id == filters["tag_id"]
                )
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        DocumentModel.title.ilike(search_term),
                        DocumentModel.content.ilike(search_term),
                        DocumentModel.summary.ilike(search_term)
                    )
                )
        
        # 加載關聯數據
        query = query.options(
            joinedload(DocumentModel.creator),
            joinedload(DocumentModel.category),
            joinedload(DocumentModel.tags)
        )
        
        # 應用分頁
        query = query.order_by(DocumentModel.created_at.desc()).offset(skip).limit(limit)
        
        # 轉換為領域實體
        return [self._to_entity(db_document) for db_document in query.all()]
    
    def delete(self, document_id: uuid.UUID) -> bool:
        """刪除文檔"""
        db_document = self.session.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if not db_document:
            return False
        
        self.session.delete(db_document)
        self.session.commit()
        return True
    
    def _to_entity(self, db_document: DocumentModel) -> Document:
        """將數據庫模型轉換為領域實體"""
        status = DocumentStatus.PUBLISHED if db_document.is_published else DocumentStatus.DRAFT
        
        document = Document(
            id=db_document.id,
            title=db_document.title,
            content=db_document.content,
            summary=db_document.summary,
            category_id=db_document.category_id,
            creator_id=db_document.creator_id,
            status=status,
            view_count=db_document.view_count,
            created_at=db_document.created_at,
            updated_at=db_document.updated_at,
            published_at=db_document.published_at,
            tags=[tag.id for tag in db_document.tags] if db_document.tags else []
        )
        
        return document
```

#### 事件發布者實現（Event Publisher Implementation）

```python
# infrastructure/messaging/event_publisher.py
from typing import Any, Dict, List, Callable
import logging

from ...application.interfaces.event_publisher import EventPublisher


class InMemoryEventPublisher(EventPublisher):
    """內存事件發布者實現"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
    
    def publish(self, event: Any) -> None:
        """發布事件"""
        event_type = event.__class__.__name__
        self.logger.info(f"Publishing event: {event_type}")
        
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error handling event {event_type}: {str(e)}")
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """訂閱事件"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        self.logger.info(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """取消訂閱事件"""
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            self.logger.info(f"Unsubscribed from event: {event_type}")
```

### 4.5 介面層（Interface Layer）

#### REST API 控制器（REST API Controller）

```python
# interfaces/api/rest/document_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, File, UploadFile
from typing import List, Optional
import uuid

from ....application.use_cases.document.create_document import CreateDocumentUseCase, CreateDocumentCommand
from ....application.use_cases.document.get_document import GetDocumentUseCase
from ....application.use_cases.document.list_documents import ListDocumentsUseCase
from ....application.use_cases.document.update_document import UpdateDocumentUseCase, UpdateDocumentCommand
from ....application.use_cases.document.delete_document import DeleteDocumentUseCase
from ....application.use_cases.document.publish_document import PublishDocumentUseCase
from ....application.use_cases.document.unpublish_document import UnpublishDocumentUseCase
from ....domain.exceptions.not_found_exception import NotFoundException
from ..schemas.document import DocumentCreateRequest, DocumentUpdateRequest, DocumentResponse, DocumentListResponse
from ..dependencies import get_current_user


router = APIRouter()


@router.get("/", response_model=List[DocumentListResponse])
async def get_documents(
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的最大記錄數"),
    category_id: Optional[uuid.UUID] = Query(None, description="按分類篩選"),
    creator_id: Optional[uuid.UUID] = Query(None, description="按創建者篩選"),
    is_published: Optional[bool] = Query(None, description="按發布狀態篩選"),
    tag_id: Optional[uuid.UUID] = Query(None, description="按標籤篩選"),
    search: Optional[str] = Query(None, description="搜索標題和內容"),
    use_case: ListDocumentsUseCase = Depends()
):
    """獲取文檔列表，支持分頁和篩選"""
    filters = {
        "category_id": category_id,
        "creator_id": creator_id,
        "is_published": is_published,
        "tag_id": tag_id,
        "search": search
    }
    documents = use_case.execute(filters, skip, limit)
    return [DocumentListResponse.from_entity(doc) for doc in documents]


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: DocumentCreateRequest,
    current_user = Depends(get_current_user),
    use_case: CreateDocumentUseCase = Depends()
):
    """創建新文檔"""
    command = CreateDocumentCommand(
        title=request.title,
        content=request.content,
        category_id=request.category_id,
        creator_id=current_user.id,
        summary=request.summary,
        tag_ids=request.tag_ids,
        is_published=request.is_published
    )
    
    try:
        document = use_case.execute(command)
        return DocumentResponse.from_entity(document)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    use_case: GetDocumentUseCase = Depends()
):
    """獲取文檔詳情"""
    try:
        document = use_case.execute(document_id)
        return DocumentResponse.from_entity(document)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
```

### 4.6 事件處理器（Event Handlers）

```python
# interfaces/events/document_event_handlers.py
import logging
from datetime import datetime

from ...domain.events.document_events import DocumentCreated, DocumentUpdated, DocumentPublished, DocumentViewed
from ...infrastructure.persistence.sqlalchemy.document_history_repository import SQLAlchemyDocumentHistoryRepository
from ...infrastructure.persistence.elasticsearch.document_search_repository import ElasticsearchDocumentSearchRepository


class DocumentEventHandlers:
    """文檔事件處理器"""
    
    def __init__(self, history_repository: SQLAlchemyDocumentHistoryRepository,
                 search_repository: ElasticsearchDocumentSearchRepository):
        self.history_repository = history_repository
        self.search_repository = search_repository
        self.logger = logging.getLogger(__name__)
    
    def handle_document_created(self, event: DocumentCreated) -> None:
        """處理文檔創建事件"""
        self.logger.info(f"Document created: {event.document_id}")
        
        # 記錄歷史
        self.history_repository.add_history(
            document_id=event.document_id,
            user_id=event.creator_id,
            action="created",
            timestamp=event.timestamp
        )
        
        # 索引文檔
        self.search_repository.index_document(event.document_id)
    
    def handle_document_updated(self, event: DocumentUpdated) -> None:
        """處理文檔更新事件"""
        self.logger.info(f"Document updated: {event.document_id}")
        
        # 記錄歷史
        self.history_repository.add_history(
            document_id=event.document_id,
            user_id=event.updater_id,
            action="updated",
            changes=event.changes,
            timestamp=event.timestamp
        )
        
        # 更新索引
        self.search_repository.index_document(event.document_id)
    
    def handle_document_published(self, event: DocumentPublished) -> None:
        """處理文檔發布事件"""
        self.logger.info(f"Document published: {event.document_id}")
        
        # 記錄歷史
        self.history_repository.add_history(
            document_id=event.document_id,
            user_id=event.publisher_id,
            action="published",
            timestamp=event.timestamp
        )
        
        # 更新索引
        self.search_repository.index_document(event.document_id)
    
    def handle_document_viewed(self, event: DocumentViewed) -> None:
        """處理文檔瀏覽事件"""
        self.logger.info(f"Document viewed: {event.document_id}")
        
        # 這裡可以實現統計、分析等功能
        pass
```

## 5. TDD 測試示例

### 5.1 領域實體測試

```python
# tests/domain/entities/test_document.py
import pytest
from datetime import datetime
import uuid

from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.domain.events.document_events import DocumentCreated, DocumentUpdated, DocumentPublished


class TestDocument:
    """文檔實體測試"""
    
    def test_create_document(self):
        """測試創建文檔"""
        # 準備測試數據
        title = "測試文檔"
        content = "這是一個測試文檔"
        category_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        summary = "測試摘要"
        
        # 執行測試
        document = Document.create(
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id,
            summary=summary
        )
        
        # 驗證結果
        assert document.title == title
        assert document.content == content
        assert document.category_id == category_id
        assert document.creator_id == creator_id
        assert document.summary == summary
        assert document.status == DocumentStatus.DRAFT
        assert document.view_count == 0
        assert document.created_at is not None
        assert document.updated_at is not None
        assert document.published_at is None
        
        # 驗證事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentCreated)
        assert events[0].document_id == document.id
        assert events[0].creator_id == creator_id
        assert events[0].title == title
        assert events[0].category_id == category_id
    
    def test_update_document(self):
        """測試更新文檔"""
        # 準備測試數據
        document = Document.create(
            title="原標題",
            content="原內容",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        
        # 清除創建事件
        document.get_events()
        
        # 執行測試
        document.update(
            title="新標題",
            content="新內容",
            summary="新摘要"
        )
        
        # 驗證結果
        assert document.title == "新標題"
        assert document.content == "新內容"
        assert document.summary == "新摘要"
        
        # 驗證事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentUpdated)
        assert events[0].document_id == document.id
        assert events[0].updater_id == document.creator_id
        assert "title" in events[0].changes
        assert "content" in events[0].changes
        assert "summary" in events[0].changes
    
    def test_publish_document(self):
        """測試發布文檔"""
        # 準備測試數據
        document = Document.create(
            title="測試文檔",
            content="這是一個測試文檔",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        
        # 清除創建事件
        document.get_events()
        
        # 執行測試
        document.publish()
        
        # 驗證結果
        assert document.status == DocumentStatus.PUBLISHED
        assert document.published_at is not None
        
        # 驗證事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentPublished)
        assert events[0].document_id == document.id
        assert events[0].publisher_id == document.creator_id
```

### 5.2 用例測試

```python
# tests/application/use_cases/document/test_create_document.py
import pytest
from unittest.mock import Mock, patch
import uuid

from src.application.use_cases.document.create_document import CreateDocumentUseCase, CreateDocumentCommand
from src.domain.entities.document import Document
from src.domain.exceptions.not_found_exception import NotFoundException


class TestCreateDocumentUseCase:
    """創建文檔用例測試"""
    
    def test_execute_success(self):
        """測試成功執行用例"""
        # 準備測試數據
        category_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        command = CreateDocumentCommand(
            title="測試文檔",
            content="這是一個測試文檔",
            category_id=category_id,
            creator_id=creator_id,
            summary="測試摘要",
            is_published=True
        )
        
        # 模擬依賴
        document_repository = Mock()
        category_repository = Mock()
        event_publisher = Mock()
        
        # 設置模擬行為
        category_repository.get_by_id.return_value = Mock(id=category_id)
        document_repository.save.return_value = Mock(id=uuid.uuid4())
        
        # 創建用例
        use_case = CreateDocumentUseCase(
            document_repository=document_repository,
            category_repository=category_repository,
            event_publisher=event_publisher
        )
        
        # 執行測試
        result = use_case.execute(command)
        
        # 驗證結果
        assert result is not None
        
        # 驗證依賴調用
        category_repository.get_by_id.assert_called_once_with(category_id)
        document_repository.save.assert_called_once()
        assert event_publisher.publish.call_count > 0
    
    def test_execute_category_not_found(self):
        """測試分類不存在的情況"""
        # 準備測試數據
        category_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        command = CreateDocumentCommand(
            title="測試文檔",
            content="這是一個測試文檔",
            category_id=category_id,
            creator_id=creator_id
        )
        
        # 模擬依賴
        document_repository = Mock()
        category_repository = Mock()
        event_publisher = Mock()
        
        # 設置模擬行為
        category_repository.get_by_id.return_value = None
        
        # 創建用例
        use_case = CreateDocumentUseCase(
            document_repository=document_repository,
            category_repository=category_repository,
            event_publisher=event_publisher
        )
        
        # 執行測試並驗證異常
        with pytest.raises(NotFoundException):
            use_case.execute(command)
        
        # 驗證依賴調用
        category_repository.get_by_id.assert_called_once_with(category_id)
        document_repository.save.assert_not_called()
        event_publisher.publish.assert_not_called()
```

## 6. 總結

通過實現乾淨架構和事件驅動設計，我們可以獲得以下好處：

1. **業務邏輯獨立**：核心業務邏輯不依賴於外部框架和工具，使其更易於測試和維護
2. **關注點分離**：每一層都有其特定的職責，使代碼更加模塊化和可維護
3. **可測試性**：通過依賴注入和接口抽象，使系統更易於測試
4. **靈活性**：可以輕鬆替換外部依賴，如數據庫、UI等
5. **可擴展性**：通過事件驅動設計，可以輕鬆添加新功能而不影響現有功能

通過TDD開發流程，我們可以確保代碼質量和功能正確性，同時提高開發效率和減少bug。

這種架構特別適合複雜的業務系統，如知識庫系統，因為它可以處理複雜的業務規則和多變的需求。