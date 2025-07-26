# Ticket 與 Knowledge 系統數據庫

## 概述

本目錄包含 Ticket 與 Knowledge 系統的數據庫相關文件，包括數據庫結構定義和遷移腳本。系統使用 PostgreSQL 作為主要數據庫，並使用 SQLAlchemy 作為 ORM 工具。

## 目錄結構

```
├── migrations/          # 數據庫遷移腳本
│   ├── ticket/          # Ticket 系統遷移
│   └── knowledge/       # Knowledge 系統遷移
└── schemas/             # 數據庫結構定義
    ├── ticket/          # Ticket 系統結構
    └── knowledge/       # Knowledge 系統結構
```

## 數據模型

### Ticket 系統數據模型

```mermaid
erDiagram
    TICKET ||--o{ TICKET_HISTORY : "has"
    TICKET ||--o{ TICKET_ATTACHMENT : "has"
    TICKET ||--o{ TICKET_COMMENT : "has"
    TICKET ||--|| TICKET_TYPE : "belongs to"
    TICKET ||--|| WORKFLOW : "follows"
    TICKET ||--|| USER : "created by"
    TICKET_TYPE ||--o{ WORKFLOW : "has"
    WORKFLOW ||--o{ WORKFLOW_STEP : "has"
    WORKFLOW_STEP ||--o{ WORKFLOW_TRANSITION : "has"
    WORKFLOW_STEP ||--o{ APPROVAL_RULE : "has"
    APPROVAL_RULE ||--o{ USER : "involves"
    APPROVAL_RULE ||--o{ ROLE : "involves"
    USER ||--o{ ROLE : "has"
    NOTIFICATION ||--|| USER : "sent to"
    NOTIFICATION ||--|| TICKET : "about"

    TICKET {
        uuid id PK
        string title
        text description
        uuid ticket_type_id FK
        uuid workflow_id FK
        uuid creator_id FK
        uuid assignee_id FK
        string status
        string priority
        datetime created_at
        datetime updated_at
        datetime due_date
    }

    TICKET_TYPE {
        uuid id PK
        string name
        text description
        boolean is_active
        jsonb fields_config
        datetime created_at
        datetime updated_at
    }

    WORKFLOW {
        uuid id PK
        string name
        text description
        uuid ticket_type_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    WORKFLOW_STEP {
        uuid id PK
        uuid workflow_id FK
        string name
        text description
        integer order
        boolean is_initial
        boolean is_final
        datetime created_at
        datetime updated_at
    }

    WORKFLOW_TRANSITION {
        uuid id PK
        uuid from_step_id FK
        uuid to_step_id FK
        string name
        text description
        jsonb conditions
        datetime created_at
        datetime updated_at
    }

    APPROVAL_RULE {
        uuid id PK
        uuid workflow_step_id FK
        string rule_type
        jsonb rule_config
        datetime created_at
        datetime updated_at
    }

    TICKET_HISTORY {
        uuid id PK
        uuid ticket_id FK
        uuid user_id FK
        string action
        jsonb changes
        datetime created_at
    }

    TICKET_ATTACHMENT {
        uuid id PK
        uuid ticket_id FK
        uuid user_id FK
        string filename
        string file_path
        string file_type
        integer file_size
        datetime created_at
    }

    TICKET_COMMENT {
        uuid id PK
        uuid ticket_id FK
        uuid user_id FK
        text content
        datetime created_at
        datetime updated_at
    }

    NOTIFICATION {
        uuid id PK
        uuid user_id FK
        uuid ticket_id FK
        string type
        string title
        text content
        boolean is_read
        datetime created_at
        datetime read_at
    }

    USER {
        uuid id PK
        string username
        string email
        string full_name
        string department
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ROLE {
        uuid id PK
        string name
        text description
        jsonb permissions
        datetime created_at
        datetime updated_at
    }
```

### Knowledge 系統數據模型

```mermaid
erDiagram
    KNOWLEDGE ||--o{ KNOWLEDGE_HISTORY : "has"
    KNOWLEDGE ||--o{ KNOWLEDGE_ATTACHMENT : "has"
    KNOWLEDGE ||--o{ KNOWLEDGE_COMMENT : "has"
    KNOWLEDGE ||--|| KNOWLEDGE_CATEGORY : "belongs to"
    KNOWLEDGE ||--|| USER : "created by"
    KNOWLEDGE ||--o{ KNOWLEDGE_TAG : "has"
    QUESTION ||--o{ ANSWER : "has"
    QUESTION ||--|| USER : "asked by"
    ANSWER ||--|| USER : "answered by"
    KNOWLEDGE_CATEGORY ||--o{ KNOWLEDGE_CATEGORY : "has"

    KNOWLEDGE {
        uuid id PK
        string title
        text content
        uuid category_id FK
        uuid creator_id FK
        boolean is_published
        integer view_count
        float rating
        datetime created_at
        datetime updated_at
        datetime published_at
    }

    KNOWLEDGE_CATEGORY {
        uuid id PK
        string name
        text description
        uuid parent_id FK
        integer order
        datetime created_at
        datetime updated_at
    }

    KNOWLEDGE_TAG {
        uuid id PK
        uuid knowledge_id FK
        string name
        datetime created_at
    }

    KNOWLEDGE_HISTORY {
        uuid id PK
        uuid knowledge_id FK
        uuid user_id FK
        text content
        jsonb changes
        datetime created_at
    }

    KNOWLEDGE_ATTACHMENT {
        uuid id PK
        uuid knowledge_id FK
        uuid user_id FK
        string filename
        string file_path
        string file_type
        integer file_size
        datetime created_at
    }

    KNOWLEDGE_COMMENT {
        uuid id PK
        uuid knowledge_id FK
        uuid user_id FK
        text content
        datetime created_at
        datetime updated_at
    }

    QUESTION {
        uuid id PK
        string title
        text content
        uuid user_id FK
        integer view_count
        boolean is_resolved
        datetime created_at
        datetime updated_at
        datetime resolved_at
    }

    ANSWER {
        uuid id PK
        uuid question_id FK
        uuid user_id FK
        text content
        boolean is_accepted
        integer vote_count
        datetime created_at
        datetime updated_at
    }

    USER {
        uuid id PK
        string username
        string email
        string full_name
        string department
        boolean is_active
        datetime created_at
        datetime updated_at
    }
```

## 數據庫遷移

系統使用 Alembic 進行數據庫遷移管理。遷移腳本位於 `migrations` 目錄下，分為 Ticket 系統和 Knowledge 系統兩部分。

### 遷移命令

```bash
# 創建新的遷移腳本
alembic revision --autogenerate -m "描述"

# 應用遷移
alembic upgrade head

# 回滾遷移
alembic downgrade -1
```

## 數據庫連接

系統使用 SQLAlchemy 進行數據庫連接和操作。連接配置位於 `shared/database` 目錄下。

### 連接示例

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/db_name"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 數據庫優化

為了確保系統性能，我們採用了以下數據庫優化策略：

1. **索引優化**：為常用查詢字段創建適當的索引
2. **分區表**：對大型表使用分區策略
3. **緩存**：使用 Redis 緩存頻繁訪問的數據
4. **讀寫分離**：考慮使用主從複製進行讀寫分離
5. **連接池**：使用連接池管理數據庫連接

## 數據安全

系統採用以下措施確保數據安全：

1. **加密存儲**：敏感數據加密存儲
2. **訪問控制**：嚴格的數據庫訪問權限控制
3. **審計日誌**：記錄關鍵數據操作的審計日誌
4. **備份策略**：定期備份數據庫
5. **數據隔離**：使用模式（Schema）進行數據隔離