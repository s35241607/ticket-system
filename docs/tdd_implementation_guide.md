# 測試驅動開發（TDD）實踐指南

本文檔詳細說明如何在知識庫系統中應用測試驅動開發（Test-Driven Development, TDD）方法，結合乾淨架構和事件驅動設計，提高代碼質量和系統穩定性。

## 目錄

- [TDD 概述](#tdd-概述)
- [TDD 在乾淨架構中的應用](#tdd-在乾淨架構中的應用)
- [TDD 實踐步驟](#tdd-實踐步驟)
- [測試類型與策略](#測試類型與策略)
- [測試工具與框架](#測試工具與框架)
- [TDD 最佳實踐](#tdd-最佳實踐)
- [常見問題與解決方案](#常見問題與解決方案)
- [案例研究](#案例研究)

## TDD 概述

測試驅動開發是一種軟體開發方法，通過先編寫測試，然後實現代碼的方式進行開發。TDD 的核心流程是「紅-綠-重構」（Red-Green-Refactor）：

1. **紅**：編寫一個測試，描述期望的功能，運行測試，確認測試失敗（紅色）。
2. **綠**：實現最簡單的代碼，使測試通過（綠色）。
3. **重構**：重構代碼，提高代碼質量，同時確保測試仍然通過。

### TDD 的優勢

1. **高質量代碼**：通過測試驅動，確保代碼的正確性和可靠性。
2. **設計改進**：通過測試驅動，促使開發者思考更好的設計。
3. **文檔作用**：測試本身可以作為代碼的文檔，說明代碼的用途和行為。
4. **重構信心**：有了測試作為保障，可以更有信心地進行重構。
5. **快速反饋**：通過測試，可以快速獲得反饋，發現問題。

## TDD 在乾淨架構中的應用

在乾淨架構中，TDD 可以應用於各個層次，從領域層到介面層。以下是在各層次應用 TDD 的方法：

### 領域層 TDD

領域層是系統的核心，包含業務實體、值物件、領域事件和儲存庫介面。在領域層應用 TDD 的步驟：

1. **編寫實體測試**：測試實體的創建、屬性和行為。
2. **編寫值物件測試**：測試值物件的創建、屬性和行為。
3. **編寫領域事件測試**：測試領域事件的創建和屬性。

### 應用層 TDD

應用層包含用例，實現業務邏輯。在應用層應用 TDD 的步驟：

1. **編寫用例測試**：測試用例的執行邏輯。
2. **模擬依賴**：使用模擬（Mock）對象模擬儲存庫和事件發布者。

### 基礎設施層 TDD

基礎設施層包含儲存庫實現、事件發布者實現等。在基礎設施層應用 TDD 的步驟：

1. **編寫儲存庫測試**：測試儲存庫的保存、獲取、列表和刪除功能。
2. **編寫事件發布者測試**：測試事件發布者的發布功能。

### 介面層 TDD

介面層包含 API 控制器、事件處理器等。在介面層應用 TDD 的步驟：

1. **編寫控制器測試**：測試控制器的請求處理和響應。
2. **編寫事件處理器測試**：測試事件處理器的事件處理邏輯。

## TDD 實踐步驟

以下是在知識庫系統中應用 TDD 的具體步驟，以文檔實體為例：

### 步驟 1：編寫領域實體測試

首先，我們編寫文檔實體的測試：

```python
# tests/domain/entities/test_document.py
import pytest
import uuid
from datetime import datetime

from src.domain.entities.document import Document
from src.domain.value_objects.document_status import DocumentStatus
from src.domain.events.document_events import DocumentCreated

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
        assert isinstance(events[0], DocumentCreated)
        assert events[0].document_id == document.id
        assert events[0].creator_id == creator_id
```

運行測試，確認測試失敗（紅色）。

### 步驟 2：實現領域實體

接下來，我們實現文檔實體：

```python
# src/domain/entities/document.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid

from ..value_objects.document_status import DocumentStatus
from ..events.document_events import DocumentCreated

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
    
    def get_events(self) -> List[any]:
        """獲取實體的領域事件"""
        events = self._events.copy()
        self._events.clear()
        return events
```

運行測試，確認測試通過（綠色）。

### 步驟 3：重構代碼

如果需要，我們可以重構代碼，提高代碼質量，同時確保測試仍然通過。

### 步驟 4：編寫更多測試

接下來，我們編寫更多測試，測試文檔實體的其他功能：

```python
# tests/domain/entities/test_document.py
# ... 前面的代碼 ...

class TestDocument:
    # ... 前面的測試 ...
    
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
        
        # 檢查事件
        events = document.get_events()
        assert len(events) == 1
        assert isinstance(events[0], DocumentUpdated)
        assert events[0].document_id == document.id
        assert events[0].updater_id == updater_id
        assert "title" in events[0].changes
        assert "content" in events[0].changes
```

運行測試，確認測試失敗（紅色）。

### 步驟 5：實現更多功能

接下來，我們實現文檔實體的更新功能：

```python
# src/domain/entities/document.py
# ... 前面的代碼 ...

from ..events.document_events import DocumentCreated, DocumentUpdated

@dataclass
class Document:
    # ... 前面的代碼 ...
    
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
```

運行測試，確認測試通過（綠色）。

### 步驟 6：編寫用例測試

接下來，我們編寫用例的測試：

```python
# tests/application/use_cases/test_document_use_cases.py
import pytest
import uuid
from unittest.mock import Mock, MagicMock

from src.domain.entities.document import Document
from src.application.use_cases.document_use_cases import CreateDocumentUseCase

class TestCreateDocumentUseCase:
    def test_execute(self):
        # Arrange
        mock_repo = Mock()
        mock_repo.save.return_value = MagicMock(spec=Document)
        
        mock_publisher = Mock()
        
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
```

運行測試，確認測試失敗（紅色）。

### 步驟 7：實現用例

接下來，我們實現用例：

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

運行測試，確認測試通過（綠色）。

### 步驟 8：編寫整合測試

最後，我們編寫整合測試，測試整個流程：

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

## 測試類型與策略

在知識庫系統中，我們可以使用以下測試類型：

### 單元測試

單元測試用於測試單個組件的功能，如實體、值物件、用例等。單元測試應該是獨立的，不依賴於外部系統。

```python
# tests/domain/entities/test_document.py
# ... 前面的代碼 ...

class TestDocument:
    # ... 前面的測試 ...
    
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
```

### 整合測試

整合測試用於測試多個組件的協作，如用例與儲存庫的協作。整合測試可以使用真實的依賴，也可以使用模擬對象。

```python
# tests/integration/test_document_repository.py
import pytest
import uuid

from src.domain.entities.document import Document
from src.infrastructure.repositories.document_repository_impl import SQLAlchemyDocumentRepository

class TestDocumentRepository:
    def test_save_and_get(self, db_session):
        # 準備
        repo = SQLAlchemyDocumentRepository(db_session)
        document = Document.create(
            title="Test Document",
            content="This is a test document",
            category_id=uuid.uuid4(),
            creator_id=uuid.uuid4()
        )
        
        # 保存文檔
        saved_document = repo.save(document)
        
        # 獲取文檔
        retrieved_document = repo.get_by_id(saved_document.id)
        
        # 驗證
        assert retrieved_document is not None
        assert retrieved_document.id == saved_document.id
        assert retrieved_document.title == saved_document.title
```

### 端到端測試

端到端測試用於測試整個系統的功能，從 API 請求到資料庫操作。端到端測試應該使用真實的依賴。

```python
# tests/e2e/test_document_api.py
import pytest
import uuid

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_create_document():
    # 準備
    data = {
        "title": "Test Document",
        "content": "This is a test document",
        "category_id": str(uuid.uuid4()),
        "creator_id": str(uuid.uuid4())
    }
    
    # 發送請求
    response = client.post("/documents", json=data)
    
    # 驗證
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["title"] == data["title"]
```

## 測試工具與框架

在知識庫系統中，我們可以使用以下測試工具和框架：

### pytest

pytest 是一個功能強大的 Python 測試框架，支持單元測試、整合測試和端到端測試。

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database import Base

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
```

### unittest.mock

unittest.mock 是 Python 標準庫中的模擬框架，可以用於模擬對象和函數。

```python
# tests/application/use_cases/test_document_use_cases.py
import pytest
import uuid
from unittest.mock import Mock, MagicMock

from src.domain.entities.document import Document
from src.application.use_cases.document_use_cases import CreateDocumentUseCase

class TestCreateDocumentUseCase:
    def test_execute(self):
        # Arrange
        mock_repo = Mock()
        mock_repo.save.return_value = MagicMock(spec=Document)
        
        mock_publisher = Mock()
        
        use_case = CreateDocumentUseCase(mock_repo, mock_publisher)
        
        # ... 測試代碼 ...
```

### FastAPI TestClient

FastAPI TestClient 是 FastAPI 提供的測試客戶端，可以用於測試 API 端點。

```python
# tests/e2e/test_document_api.py
import pytest
import uuid

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_create_document():
    # ... 測試代碼 ...
```

## TDD 最佳實踐

在知識庫系統中應用 TDD 時，可以遵循以下最佳實踐：

### 1. 從簡單的測試開始

從簡單的測試開始，逐步增加複雜性。例如，先測試實體的創建，然後測試實體的行為。

### 2. 使用描述性的測試名稱

使用描述性的測試名稱，清楚地表達測試的目的。例如，`test_create_document` 表示測試文檔的創建。

### 3. 遵循 AAA 模式

遵循 Arrange-Act-Assert（AAA）模式，使測試結構清晰：

- **Arrange**：準備測試數據和環境。
- **Act**：執行被測試的代碼。
- **Assert**：驗證結果是否符合預期。

### 4. 使用模擬對象

使用模擬對象模擬依賴，使測試獨立於外部系統。例如，使用模擬儲存庫和事件發布者。

### 5. 測試邊界條件

測試邊界條件和異常情況，確保代碼在各種情況下都能正常工作。例如，測試文檔標題為空的情況。

### 6. 保持測試獨立

保持測試獨立，不依賴於其他測試的結果。每個測試都應該能夠獨立運行。

### 7. 使用夾具（Fixtures）

使用夾具準備測試數據和環境，避免重複代碼。例如，使用夾具準備資料庫會話。

### 8. 定期運行測試

定期運行測試，確保代碼的正確性。可以使用持續整合（CI）系統自動運行測試。

## 常見問題與解決方案

在應用 TDD 時，可能會遇到以下問題：

### 1. 測試太慢

**問題**：隨著測試數量的增加，測試運行時間可能會變得很長。

**解決方案**：
- 使用更快的測試框架，如 pytest。
- 使用模擬對象代替真實依賴。
- 使用並行測試運行。
- 只運行受影響的測試。

### 2. 測試太脆弱

**問題**：測試可能會因為小的代碼變化而失敗。

**解決方案**：
- 測試行為而不是實現細節。
- 使用更高層次的抽象。
- 避免過度指定。

### 3. 測試覆蓋率不足

**問題**：測試可能無法覆蓋所有代碼路徑。

**解決方案**：
- 使用測試覆蓋率工具，如 pytest-cov。
- 識別未覆蓋的代碼路徑。
- 編寫更多測試。

### 4. 測試維護成本高

**問題**：隨著代碼的變化，測試可能需要頻繁更新。

**解決方案**：
- 測試行為而不是實現細節。
- 使用更高層次的抽象。
- 避免重複代碼。

## 案例研究

以下是在知識庫系統中應用 TDD 的案例研究：

### 案例 1：文檔創建功能

**需求**：用戶可以創建新文檔，包括標題、內容、分類和標籤。

**TDD 流程**：

1. **編寫測試**：編寫測試，描述文檔創建功能。
2. **實現代碼**：實現文檔實體和創建文檔的用例。
3. **重構代碼**：重構代碼，提高代碼質量。

**結果**：
- 高質量的文檔創建功能。
- 清晰的代碼結構。
- 完整的測試覆蓋率。

### 案例 2：文檔搜索功能

**需求**：用戶可以搜索文檔，包括標題、內容和標籤。

**TDD 流程**：

1. **編寫測試**：編寫測試，描述文檔搜索功能。
2. **實現代碼**：實現文檔搜索的用例和儲存庫方法。
3. **重構代碼**：重構代碼，提高代碼質量。

**結果**：
- 高效的文檔搜索功能。
- 清晰的代碼結構。
- 完整的測試覆蓋率。

## 結論

測試驅動開發是一種有效的軟體開發方法，可以幫助我們構建高質量、可維護的系統。通過先編寫測試，然後實現代碼的方式進行開發，我們可以確保代碼的正確性和可靠性，並促使我們思考更好的設計。

在知識庫系統中應用 TDD，結合乾淨架構和事件驅動設計，可以幫助我們構建一個穩定、可靠、可擴展的系統。通過遵循 TDD 的最佳實踐，我們可以提高代碼質量，減少技術債務，並使系統更加穩定和可靠。