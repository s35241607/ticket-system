# 乾淨架構與事件驅動設計實現指南

本文檔詳細說明如何將現有的知識庫系統重構為採用乾淨架構（Clean Architecture）和事件驅動設計（Event-Driven Design）的系統，並融入測試驅動開發（TDD）的開發方法。

## 目錄

- [乾淨架構概述](#乾淨架構概述)
- [事件驅動設計概述](#事件驅動設計概述)
- [測試驅動開發概述](#測試驅動開發概述)
- [實現步驟](#實現步驟)
- [目錄結構](#目錄結構)
- [代碼示例](#代碼示例)
- [測試策略](#測試策略)
- [遷移策略](#遷移策略)
- [效益分析](#效益分析)

## 乾淨架構概述

乾淨架構是一種軟體設計方法，旨在將系統分為不同的層次，每個層次都有特定的職責，並且依賴關係只能從外層指向內層。

### 核心原則

1. **依賴倒置原則**：高層模組不應該依賴低層模組，兩者都應該依賴抽象。
2. **關注點分離**：將系統分為不同的層次，每個層次都有特定的職責。
3. **業務邏輯獨立**：業務邏輯不應該依賴於框架、資料庫或 UI。

### 架構層次

1. **領域層（Domain Layer）**
   - 包含業務實體、值物件、領域事件和儲存庫介面
   - 代表系統的核心業務邏輯和規則
   - 不依賴於任何外部框架或技術

2. **應用層（Application Layer）**
   - 包含用例（Use Cases），實現業務邏輯
   - 協調領域物件以完成特定的應用任務
   - 依賴於領域層，但不依賴於基礎設施層

3. **基礎設施層（Infrastructure Layer）**
   - 包含儲存庫實現、事件發布者實現等
   - 提供與外部系統的整合
   - 依賴於領域層和應用層

4. **介面層（Interface Layer）**
   - 包含 API 控制器、事件處理器等
   - 處理外部請求並將其轉換為應用層的調用
   - 依賴於應用層

## 事件驅動設計概述

事件驅動設計是一種軟體設計方法，通過事件的發布和訂閱實現系統組件之間的鬆耦合通信。

### 核心概念

1. **領域事件（Domain Events）**：代表系統中發生的重要業務事件，如「文檔已創建」、「文檔已發布」等。
2. **事件發布者（Event Publisher）**：負責發布事件。
3. **事件處理器（Event Handler）**：負責處理特定類型的事件。
4. **事件總線（Event Bus）**：負責將事件從發布者傳遞給處理器。

### 事件驅動的優勢

1. **鬆耦合**：系統組件之間通過事件進行通信，減少直接依賴。
2. **可擴展性**：可以輕鬆添加新的事件處理器，而不需要修改現有代碼。
3. **可測試性**：可以獨立測試事件發布者和處理器。
4. **異步處理**：可以實現異步處理，提高系統性能。

## 測試驅動開發概述

測試驅動開發（TDD）是一種軟體開發方法，通過先編寫測試，然後實現代碼的方式進行開發。

### TDD 流程

1. **編寫測試**：首先編寫一個測試，描述期望的功能。
2. **運行測試**：運行測試，確認測試失敗。
3. **實現代碼**：實現最簡單的代碼，使測試通過。
4. **重構代碼**：重構代碼，提高代碼質量，同時確保測試仍然通過。
5. **重複以上步驟**：繼續編寫新的測試，實現新的功能。

### TDD 的優勢

1. **高質量代碼**：通過測試驅動，確保代碼的正確性和可靠性。
2. **設計改進**：通過測試驅動，促使開發者思考更好的設計。
3. **文檔作用**：測試本身可以作為代碼的文檔，說明代碼的用途和行為。
4. **重構信心**：有了測試作為保障，可以更有信心地進行重構。

## 實現步驟

### 1. 定義領域模型

首先，我們需要定義系統的領域模型，包括實體、值物件和領域事件。

#### 實體（Entities）

實體是具有唯一標識的物件，如文檔、用戶等。

```python
# src/domain/entities/document.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

from ..value_objects.document_status import DocumentStatus
from ..events.document_events import DocumentCreated, DocumentUpdated

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
    _events: List[any] = field(default_factory=list, init=False)
    
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
```

#### 值物件（Value Objects）

值物件是沒有唯一標識的物件，如文檔狀態、日期等。

```python
# src/domain/value_objects/document_status.py
from enum import Enum, auto

class DocumentStatus(Enum):
    DRAFT = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()
```

#### 領域事件（Domain Events）

領域事件代表系統中發生的重要業務事件。

```python
# src/domain/events/document_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
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
```

### 2. 定義儲存庫介面

儲存庫介面定義了如何存取和持久化領域物件。

```python
# src/domain/repositories/document_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from ..entities.document import Document

class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> Document:
        pass
    
    @abstractmethod
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        pass
    
    @abstractmethod
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        pass
    
    @abstractmethod
    def delete(self, document_id: uuid.UUID) -> bool:
        pass
```

### 3. 定義事件發布者介面

事件發布者介面定義了如何發布領域事件。

```python
# src/domain/events/event_publisher.py
from abc import ABC, abstractmethod
from typing import List

from .base_event import DomainEvent

class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        pass
    
    @abstractmethod
    def publish_all(self, events: List[DomainEvent]) -> None:
        pass
```

### 4. 實現用例

用例實現系統的業務邏輯，協調領域物件完成特定任務。

```python
# src/application/use_cases/document_use_cases.py
from typing import List, Optional, Dict, Any
import uuid

from ...domain.entities.document import Document
from ...domain.repositories.document_repository import DocumentRepository
from ...domain.events.event_publisher import EventPublisher

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
```

### 5. 實現儲存庫

儲存庫實現定義了如何實際存取和持久化領域物件。

```python
# src/infrastructure/repositories/document_repository_impl.py
from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy.orm import Session

from ...domain.entities.document import Document
from ...domain.repositories.document_repository import DocumentRepository

class SQLAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, document: Document) -> Document:
        # 實現保存邏輯
        pass
    
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        # 實現獲取邏輯
        pass
    
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        # 實現列表邏輯
        pass
    
    def delete(self, document_id: uuid.UUID) -> bool:
        # 實現刪除邏輯
        pass
```

### 6. 實現事件發布者

事件發布者實現定義了如何實際發布領域事件。

```python
# src/infrastructure/events/event_publisher_impl.py
from typing import List, Dict, Type, Callable
import logging

from ...domain.events.base_event import DomainEvent
from ...domain.events.event_publisher import EventPublisher

class InMemoryEventPublisher(EventPublisher):
    def __init__(self):
        self.handlers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_handler(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        self.logger.info(f"Publishing event: {event_type.__name__}")
        
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error handling event {event_type.__name__}: {str(e)}")
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        for event in events:
            self.publish(event)
```

### 7. 實現 API 控制器

API 控制器處理外部請求並將其轉換為應用層的調用。

```python
# src/interface/api/document_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from ...application.use_cases.document_use_cases import CreateDocumentUseCase
from ...infrastructure.repositories.document_repository_impl import SQLAlchemyDocumentRepository
from ...infrastructure.events.event_publisher_impl import InMemoryEventPublisher

router = APIRouter()

# 創建事件發布者
event_publisher = InMemoryEventPublisher()

# 依賴注入函數
def get_document_repository(db: Session = Depends(get_db)):
    return SQLAlchemyDocumentRepository(db)

def get_create_document_use_case(repo = Depends(get_document_repository)):
    return CreateDocumentUseCase(repo, event_publisher)

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    use_case: CreateDocumentUseCase = Depends(get_create_document_use_case)
):
    try:
        created_document = use_case.execute(
            title=document.title,
            content=document.content,
            category_id=uuid.UUID(document.category_id),
            creator_id=uuid.UUID(document.creator_id),
            summary=document.summary,
            tags=[uuid.UUID(tag_id) for tag_id in document.tags] if document.tags else None
        )
        
        return _document_entity_to_response(created_document)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### 8. 實現事件處理器

事件處理器處理特定類型的事件。

```python
# src/interface/event_handlers/document_event_handlers.py
import logging

from ...domain.events.document_events import DocumentCreated, DocumentUpdated

def document_created_handler(event: DocumentCreated) -> None:
    logger = logging.getLogger(__name__)
    logger.info(f"Document created: {event.document_id} by {event.creator_id}")
    # 這裡可以添加更多邏輯，如發送通知、更新索引等

def document_updated_handler(event: DocumentUpdated) -> None:
    logger = logging.getLogger(__name__)
    logger.info(f"Document updated: {event.document_id} by {event.updater_id}")
    # 這裡可以添加更多邏輯，如發送通知、更新索引等
```

## 目錄結構

```
src/
  domain/
    entities/          # 領域實體
      document.py
      user.py
      ...
    value_objects/     # 值物件
      document_status.py
      ...
    events/            # 領域事件
      base_event.py
      document_events.py
      event_publisher.py
      ...
    repositories/      # 儲存庫介面
      document_repository.py
      ...
  application/
    use_cases/         # 用例
      document_use_cases.py
      ...
  infrastructure/
    repositories/      # 儲存庫實現
      document_repository_impl.py
      ...
    events/            # 事件發布者實現
      event_publisher_impl.py
      ...
  interface/
    api/               # API 控制器
      document_controller.py
      ...
    event_handlers/    # 事件處理器
      document_event_handlers.py
      ...

tests/
  domain/             # 領域層測試
    entities/
      test_document.py
      ...
  application/        # 應用層測試
    use_cases/
      test_document_use_cases.py
      ...
  infrastructure/     # 基礎設施層測試
    repositories/
      test_document_repository_impl.py
      ...
  interface/          # 介面層測試
    api/
      test_document_controller.py
      ...
  integration/        # 整合測試
    test_document_flow.py
    ...
```

## 測試策略

### 單元測試

單元測試用於測試單個組件的功能，如實體、值物件、用例等。

```python
# tests/domain/entities/test_document.py
import pytest
import uuid
from datetime import datetime

from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus

class TestDocument:
    def test_create_document(self):
        # Arrange
        title = "Test Document"
        content = "This is a test document"
        category_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        
        # Act
        document = Document.create(
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id
        )
        
        # Assert
        assert document.title == title
        assert document.content == content
        assert document.category_id == category_id
        assert document.creator_id == creator_id
        assert document.status == DocumentStatus.DRAFT
        assert document.view_count == 0
        
        # 檢查事件
        events = document.get_events()
        assert len(events) == 1
        assert events[0].document_id == document.id
        assert events[0].creator_id == creator_id
```

### 整合測試

整合測試用於測試多個組件的協作，如用例與儲存庫的協作。

```python
# tests/integration/test_document_flow.py
import pytest
import uuid

from src.domain.entities.document import Document
from src.infrastructure.repositories.document_repository_impl import SQLAlchemyDocumentRepository
from src.infrastructure.events.event_publisher_impl import InMemoryEventPublisher
from src.application.use_cases.document_use_cases import CreateDocumentUseCase, GetDocumentUseCase

class TestDocumentFlow:
    def test_document_lifecycle(self, db_session):
        # 準備
        repo = SQLAlchemyDocumentRepository(db_session)
        publisher = InMemoryEventPublisher()
        create_use_case = CreateDocumentUseCase(repo, publisher)
        get_use_case = GetDocumentUseCase(repo, publisher)
        
        # 創建文檔
        document = create_use_case.execute(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        
        # 獲取文檔
        retrieved_document = get_use_case.execute(document.id)
        
        # 驗證
        assert retrieved_document is not None
        assert retrieved_document.id == document.id
        assert retrieved_document.title == document.title
```

## 遷移策略

將現有系統遷移到乾淨架構和事件驅動設計需要一個漸進的過程。以下是建議的遷移步驟：

1. **識別領域模型**：識別系統中的核心實體和值物件。
2. **定義領域事件**：識別系統中的重要業務事件。
3. **實現領域層**：實現領域實體、值物件和事件。
4. **定義儲存庫介面**：定義如何存取和持久化領域物件的介面。
5. **實現用例**：實現系統的業務邏輯。
6. **實現基礎設施層**：實現儲存庫和事件發布者。
7. **實現介面層**：實現 API 控制器和事件處理器。
8. **編寫測試**：為每個組件編寫測試。
9. **漸進式替換**：漸進式替換現有系統的組件。

## 效益分析

採用乾淨架構和事件驅動設計可以帶來以下效益：

1. **可維護性**：系統分層清晰，每個組件都有明確的職責，使代碼更容易維護。
2. **可測試性**：每個組件都可以獨立測試，提高代碼質量。
3. **可擴展性**：可以輕鬆添加新功能，而不需要修改現有代碼。
4. **業務邏輯獨立**：業務邏輯不依賴於框架、資料庫或 UI，使系統更加穩定。
5. **鬆耦合**：系統組件之間通過事件進行通信，減少直接依賴。
6. **可追蹤性**：通過事件可以追蹤系統中的業務活動。

## 結論

乾淨架構和事件驅動設計是一種強大的軟體設計方法，可以幫助我們構建可維護、可測試和可擴展的系統。通過採用這些方法，我們可以提高代碼質量，減少技術債務，並使系統更加穩定和可靠。

測試驅動開發是一種有效的開發方法，可以幫助我們確保代碼的正確性和可靠性。通過先編寫測試，然後實現代碼的方式進行開發，我們可以提高代碼質量，並使系統更加穩定。