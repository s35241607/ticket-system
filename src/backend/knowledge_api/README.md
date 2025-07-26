# Knowledge API 系統

## 概述

本目錄包含 Knowledge 系統的後端 API 代碼，使用 FastAPI + SQLAlchemy + PostgreSQL 開發。Knowledge API 系統提供知識庫管理的核心功能，包括文檔管理、問答管理、分類管理和搜索功能。

## 目錄結構

```
├── api/                # API 路由
│   ├── v1/             # API v1 版本
│   │   ├── document.py # 文檔 API
│   │   ├── question.py # 問答 API
│   │   ├── category.py # 分類 API
│   │   ├── search.py   # 搜索 API
│   │   ├── tag.py      # 標籤 API
│   │   └── user.py     # 用戶 API
│   └── deps.py         # 依賴注入
├── core/               # 核心模塊
│   ├── config.py       # 配置
│   ├── security.py     # 安全
│   └── logging.py      # 日誌
├── db/                 # 數據庫
│   ├── base.py         # 基礎模型
│   ├── session.py      # 會話
│   └── init_db.py      # 初始化數據庫
├── models/             # 數據模型
│   ├── document.py     # 文檔模型
│   ├── question.py     # 問答模型
│   ├── category.py     # 分類模型
│   ├── tag.py          # 標籤模型
│   └── user.py         # 用戶模型
├── schemas/            # 數據模式
│   ├── document.py     # 文檔模式
│   ├── question.py     # 問答模式
│   ├── category.py     # 分類模式
│   ├── tag.py          # 標籤模式
│   └── user.py         # 用戶模式
├── services/           # 服務
│   ├── document.py     # 文檔服務
│   ├── question.py     # 問答服務
│   ├── category.py     # 分類服務
│   ├── search.py       # 搜索服務
│   └── tag.py          # 標籤服務
├── utils/              # 工具
│   ├── search.py       # 搜索工具
│   ├── storage.py      # 存儲工具
│   └── validation.py   # 驗證工具
├── tests/              # 測試
│   ├── api/            # API 測試
│   ├── services/       # 服務測試
│   └── conftest.py     # 測試配置
├── main.py             # 主程序
└── requirements.txt    # 依賴
```

## API 設計

### 文檔 API

#### 獲取文檔列表

```
GET /api/v1/documents
```

**查詢參數：**

- `category_id`: 分類 ID
- `tag`: 標籤
- `q`: 搜索關鍵詞
- `page`: 頁碼
- `per_page`: 每頁數量
- `sort`: 排序字段
- `order`: 排序方向 (asc, desc)

**響應：**

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "文檔標題",
      "summary": "文檔摘要",
      "category": {
        "id": "uuid",
        "name": "分類名稱"
      },
      "creator": {
        "id": "uuid",
        "full_name": "創建者姓名"
      },
      "view_count": 100,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "pages": 10
}
```

#### 獲取文檔詳情

```
GET /api/v1/documents/{document_id}
```

**響應：**

```json
{
  "id": "uuid",
  "title": "文檔標題",
  "content": "文檔內容",
  "category": {
    "id": "uuid",
    "name": "分類名稱"
  },
  "creator": {
    "id": "uuid",
    "full_name": "創建者姓名"
  },
  "tags": [
    {
      "id": "uuid",
      "name": "標籤名稱"
    }
  ],
  "attachments": [
    {
      "id": "uuid",
      "filename": "附件名稱",
      "file_type": "附件類型",
      "file_size": 1024,
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "comments": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "full_name": "用戶姓名"
      },
      "content": "評論內容",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "view_count": 100,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 創建文檔

```
POST /api/v1/documents
```

**請求體：**

```json
{
  "title": "文檔標題",
  "content": "文檔內容",
  "category_id": "uuid",
  "tags": ["標籤1", "標籤2"],
  "is_published": true
}
```

**響應：**

```json
{
  "id": "uuid",
  "title": "文檔標題",
  "content": "文檔內容",
  "category": {
    "id": "uuid",
    "name": "分類名稱"
  },
  "creator": {
    "id": "uuid",
    "full_name": "創建者姓名"
  },
  "tags": [
    {
      "id": "uuid",
      "name": "標籤1"
    },
    {
      "id": "uuid",
      "name": "標籤2"
    }
  ],
  "is_published": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 更新文檔

```
PUT /api/v1/documents/{document_id}
```

**請求體：**

```json
{
  "title": "更新的文檔標題",
  "content": "更新的文檔內容",
  "category_id": "uuid",
  "tags": ["標籤1", "標籤2"],
  "is_published": true
}
```

**響應：**

```json
{
  "id": "uuid",
  "title": "更新的文檔標題",
  "content": "更新的文檔內容",
  "category": {
    "id": "uuid",
    "name": "分類名稱"
  },
  "creator": {
    "id": "uuid",
    "full_name": "創建者姓名"
  },
  "tags": [
    {
      "id": "uuid",
      "name": "標籤1"
    },
    {
      "id": "uuid",
      "name": "標籤2"
    }
  ],
  "is_published": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 刪除文檔

```
DELETE /api/v1/documents/{document_id}
```

**響應：**

```json
{
  "success": true
}
```

#### 上傳附件

```
POST /api/v1/documents/{document_id}/attachments
```

**請求體：**

```
Content-Type: multipart/form-data
file: <file>
```

**響應：**

```json
{
  "id": "uuid",
  "document_id": "uuid",
  "filename": "附件名稱",
  "file_type": "附件類型",
  "file_size": 1024,
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### 添加評論

```
POST /api/v1/documents/{document_id}/comments
```

**請求體：**

```json
{
  "content": "評論內容"
}
```

**響應：**

```json
{
  "id": "uuid",
  "document_id": "uuid",
  "user": {
    "id": "uuid",
    "full_name": "用戶姓名"
  },
  "content": "評論內容",
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### 獲取文檔歷史記錄

```
GET /api/v1/documents/{document_id}/history
```

**響應：**

```json
{
  "items": [
    {
      "id": "uuid",
      "document_id": "uuid",
      "user": {
        "id": "uuid",
        "full_name": "用戶姓名"
      },
      "changes": {
        "title": {
          "old": "舊標題",
          "new": "新標題"
        },
        "content": {
          "old": "舊內容",
          "new": "新內容"
        }
      },
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 10
}
```

### 問答 API

#### 獲取問題列表

```
GET /api/v1/questions
```

**查詢參數：**

- `q`: 搜索關鍵詞
- `is_resolved`: 是否已解決
- `page`: 頁碼
- `per_page`: 每頁數量
- `sort`: 排序字段
- `order`: 排序方向 (asc, desc)

**響應：**

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "問題標題",
      "user": {
        "id": "uuid",
        "full_name": "用戶姓名"
      },
      "is_resolved": false,
      "answer_count": 5,
      "view_count": 100,
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "pages": 10
}
```

#### 獲取問題詳情

```
GET /api/v1/questions/{question_id}
```

**響應：**

```json
{
  "id": "uuid",
  "title": "問題標題",
  "content": "問題內容",
  "user": {
    "id": "uuid",
    "full_name": "用戶姓名"
  },
  "is_resolved": false,
  "accepted_answer_id": null,
  "view_count": 100,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 創建問題

```
POST /api/v1/questions
```

**請求體：**

```json
{
  "title": "問題標題",
  "content": "問題內容"
}
```

**響應：**

```json
{
  "id": "uuid",
  "title": "問題標題",
  "content": "問題內容",
  "user": {
    "id": "uuid",
    "full_name": "用戶姓名"
  },
  "is_resolved": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 更新問題

```
PUT /api/v1/questions/{question_id}
```

**請求體：**

```json
{
  "title": "更新的問題標題",
  "content": "更新的問題內容"
}
```

**響應：**

```json
{
  "id": "uuid",
  "title": "更新的問題標題",
  "content": "更新的問題內容",
  "user": {
    "id": "uuid",
    "full_name": "用戶姓名"
  },
  "is_resolved": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 刪除問題

```
DELETE /api/v1/questions/{question_id}
```

**響應：**

```json
{
  "success": true
}
```

#### 獲取問題的回答列表

```
GET /api/v1/questions/{question_id}/answers
```

**響應：**

```json
{
  "items": [
    {
      "id": "uuid",
      "content": "回答內容",
      "user": {
        "id": "uuid",
        "full_name": "用戶姓名"
      },
      "is_accepted": false,
      "vote_count": 10,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z"
    }
  ],
  "total": 5
}
```

#### 創建回答

```
POST /api/v1/questions/{question_id}/answers
```

**請求體：**

```json
{
  "content": "回答內容"
}
```

**響應：**

```json
{
  "id": "uuid",
  "question_id": "uuid",
  "content": "回答內容",
  "user": {
    "id": "uuid",
    "full_name": "用戶姓名"
  },
  "is_accepted": false,
  "vote_count": 0,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 更新回答

```
PUT /api/v1/answers/{answer_id}
```

**請求體：**

```json
{
  "content": "更新的回答內容"
}
```

**響應：**

```json
{
  "id": "uuid",
  "question_id": "uuid",
  "content": "更新的回答內容",
  "user": {
    "id": "uuid",
    "full_name": "用戶姓名"
  },
  "is_accepted": false,
  "vote_count": 0,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 刪除回答

```
DELETE /api/v1/answers/{answer_id}
```

**響應：**

```json
{
  "success": true
}
```

#### 投票回答

```
POST /api/v1/answers/{answer_id}/vote
```

**請求體：**

```json
{
  "value": 1  // 1 表示贊成，-1 表示反對
}
```

**響應：**

```json
{
  "id": "uuid",
  "vote_count": 11
}
```

#### 接受回答

```
POST /api/v1/questions/{question_id}/accept
```

**請求體：**

```json
{
  "answer_id": "uuid"
}
```

**響應：**

```json
{
  "success": true
}
```

### 分類 API

#### 獲取分類列表

```
GET /api/v1/categories
```

**響應：**

```json
[
  {
    "id": "uuid",
    "name": "分類名稱",
    "description": "分類描述",
    "parent_id": null,
    "children": [
      {
        "id": "uuid",
        "name": "子分類名稱",
        "description": "子分類描述",
        "parent_id": "uuid",
        "children": []
      }
    ]
  }
]
```

#### 獲取分類詳情

```
GET /api/v1/categories/{category_id}
```

**響應：**

```json
{
  "id": "uuid",
  "name": "分類名稱",
  "description": "分類描述",
  "parent_id": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 創建分類

```
POST /api/v1/categories
```

**請求體：**

```json
{
  "name": "分類名稱",
  "description": "分類描述",
  "parent_id": null
}
```

**響應：**

```json
{
  "id": "uuid",
  "name": "分類名稱",
  "description": "分類描述",
  "parent_id": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 更新分類

```
PUT /api/v1/categories/{category_id}
```

**請求體：**

```json
{
  "name": "更新的分類名稱",
  "description": "更新的分類描述",
  "parent_id": null
}
```

**響應：**

```json
{
  "id": "uuid",
  "name": "更新的分類名稱",
  "description": "更新的分類描述",
  "parent_id": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 刪除分類

```
DELETE /api/v1/categories/{category_id}
```

**響應：**

```json
{
  "success": true
}
```

### 搜索 API

#### 全文搜索

```
GET /api/v1/search
```

**查詢參數：**

- `q`: 搜索關鍵詞
- `type`: 搜索類型 (document, question, answer, all)
- `category_id`: 分類 ID
- `page`: 頁碼
- `per_page`: 每頁數量

**響應：**

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "文檔標題",
      "content": "文檔內容片段...",
      "type": "document",
      "url": "/documents/uuid",
      "highlights": ["關鍵詞1", "關鍵詞2"],
      "score": 0.95,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z"
    },
    {
      "id": "uuid",
      "title": "問題標題",
      "content": "問題內容片段...",
      "type": "question",
      "url": "/questions/uuid",
      "highlights": ["關鍵詞1", "關鍵詞2"],
      "score": 0.85,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "pages": 10
}
```

## 數據模型

### 文檔模型

```python
# models/document.py
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    published_at = Column(DateTime, nullable=True)

    category = relationship("Category", back_populates="documents")
    creator = relationship("User", back_populates="documents")
    attachments = relationship("DocumentAttachment", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("DocumentComment", back_populates="document", cascade="all, delete-orphan")
    history = relationship("DocumentHistory", back_populates="document", cascade="all, delete-orphan")
    tags = relationship("DocumentTag", back_populates="document", cascade="all, delete-orphan")


class DocumentAttachment(Base):
    __tablename__ = "document_attachments"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    document = relationship("Document", back_populates="attachments")
    user = relationship("User")


class DocumentComment(Base):
    __tablename__ = "document_comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    document = relationship("Document", back_populates="comments")
    user = relationship("User")


class DocumentHistory(Base):
    __tablename__ = "document_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    changes = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=func.now())

    document = relationship("Document", back_populates="history")
    user = relationship("User")


class DocumentTag(Base):
    __tablename__ = "document_tags"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    document = relationship("Document", back_populates="tags")
```

### 問答模型

```python
# models/question.py
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_resolved = Column(Boolean, default=False)
    accepted_answer_id = Column(String, nullable=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_accepted = Column(Boolean, default=False)
    vote_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")
    votes = relationship("AnswerVote", back_populates="answer", cascade="all, delete-orphan")


class AnswerVote(Base):
    __tablename__ = "answer_votes"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    answer_id = Column(String, ForeignKey("answers.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    value = Column(Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = Column(DateTime, default=func.now())

    answer = relationship("Answer", back_populates="votes")
    user = relationship("User")
```

### 分類模型

```python
# models/category.py
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(String, ForeignKey("categories.id"), nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
    documents = relationship("Document", back_populates="category")
```

### 用戶模型

```python
# models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    documents = relationship("Document", back_populates="creator")
    questions = relationship("Question", back_populates="user")
    answers = relationship("Answer", back_populates="user")
```

## 服務實現

### 文檔服務

```python
# services/document.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile
import json

from models.document import Document, DocumentAttachment, DocumentComment, DocumentHistory, DocumentTag
from schemas.document import DocumentCreate, DocumentUpdate
from utils.storage import save_file


class DocumentService:
    @staticmethod
    def get_documents(
        db: Session,
        category_id: Optional[str] = None,
        tag: Optional[str] = None,
        q: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[Document]:
        query = db.query(Document)

        if category_id:
            query = query.filter(Document.category_id == category_id)

        if tag:
            query = query.join(DocumentTag).filter(DocumentTag.name == tag)

        if q:
            query = query.filter(
                Document.title.ilike(f"%{q}%") | Document.content.ilike(f"%{q}%")
            )

        if sort:
            if order and order.lower() == "desc":
                query = query.order_by(getattr(Document, sort).desc())
            else:
                query = query.order_by(getattr(Document, sort))
        else:
            query = query.order_by(Document.updated_at.desc())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_document(db: Session, document_id: str) -> Optional[Document]:
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def create_document(
        db: Session, document: DocumentCreate, creator_id: str
    ) -> Document:
        db_document = Document(
            title=document.title,
            content=document.content,
            category_id=document.category_id,
            creator_id=creator_id,
            is_published=document.is_published,
        )
        db.add(db_document)
        db.flush()

        if document.tags:
            for tag_name in document.tags:
                db_tag = DocumentTag(document_id=db_document.id, name=tag_name)
                db.add(db_tag)

        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def update_document(
        db: Session, document_id: str, document: DocumentUpdate, user_id: str
    ) -> Optional[Document]:
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if not db_document:
            return None

        # Save document history
        changes = {}
        if document.title != db_document.title:
            changes["title"] = {"old": db_document.title, "new": document.title}
        if document.content != db_document.content:
            changes["content"] = {"old": db_document.content, "new": document.content}
        if document.category_id != db_document.category_id:
            changes["category_id"] = {
                "old": db_document.category_id,
                "new": document.category_id,
            }
        if document.is_published != db_document.is_published:
            changes["is_published"] = {
                "old": db_document.is_published,
                "new": document.is_published,
            }

        if changes:
            db_history = DocumentHistory(
                document_id=document_id,
                user_id=user_id,
                content=db_document.content,
                changes=json.dumps(changes),
            )
            db.add(db_history)

        # Update document
        for key, value in document.dict(exclude_unset=True).items():
            if key != "tags":
                setattr(db_document, key, value)

        # Update tags
        if document.tags is not None:
            # Remove existing tags
            db.query(DocumentTag).filter(DocumentTag.document_id == document_id).delete()

            # Add new tags
            for tag_name in document.tags:
                db_tag = DocumentTag(document_id=document_id, name=tag_name)
                db.add(db_tag)

        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def delete_document(db: Session, document_id: str) -> bool:
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if not db_document:
            return False

        db.delete(db_document)
        db.commit()
        return True

    @staticmethod
    def upload_attachment(
        db: Session, document_id: str, file: UploadFile, user_id: str
    ) -> Optional[DocumentAttachment]:
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if not db_document:
            return None

        file_path = save_file(file, f"documents/{document_id}/attachments")
        db_attachment = DocumentAttachment(
            document_id=document_id,
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_type=file.content_type,
            file_size=file.size,
        )
        db.add(db_attachment)
        db.commit()
        db.refresh(db_attachment)
        return db_attachment

    @staticmethod
    def add_comment(
        db: Session, document_id: str, content: str, user_id: str
    ) -> Optional[DocumentComment]:
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if not db_document:
            return None

        db_comment = DocumentComment(
            document_id=document_id, user_id=user_id, content=content
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_document_history(db: Session, document_id: str) -> List[DocumentHistory]:
        return (
            db.query(DocumentHistory)
            .filter(DocumentHistory.document_id == document_id)
            .order_by(DocumentHistory.created_at.desc())
            .all()
        )

    @staticmethod
    def increment_view_count(db: Session, document_id: str) -> None:
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            db_document.view_count += 1
            db.commit()
```

### 問答服務

```python
# services/question.py
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from models.question import Question, Answer, AnswerVote
from schemas.question import QuestionCreate, QuestionUpdate, AnswerCreate, AnswerUpdate


class QuestionService:
    @staticmethod
    def get_questions(
        db: Session,
        q: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> List[Question]:
        query = db.query(Question)

        if q:
            query = query.filter(
                Question.title.ilike(f"%{q}%") | Question.content.ilike(f"%{q}%")
            )

        if is_resolved is not None:
            query = query.filter(Question.is_resolved == is_resolved)

        if sort:
            if order and order.lower() == "desc":
                query = query.order_by(getattr(Question, sort).desc())
            else:
                query = query.order_by(getattr(Question, sort))
        else:
            query = query.order_by(Question.created_at.desc())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_question(db: Session, question_id: str) -> Optional[Question]:
        return db.query(Question).filter(Question.id == question_id).first()

    @staticmethod
    def create_question(db: Session, question: QuestionCreate, user_id: str) -> Question:
        db_question = Question(
            title=question.title, content=question.content, user_id=user_id
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    @staticmethod
    def update_question(
        db: Session, question_id: str, question: QuestionUpdate
    ) -> Optional[Question]:
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None

        for key, value in question.dict(exclude_unset=True).items():
            setattr(db_question, key, value)

        db.commit()
        db.refresh(db_question)
        return db_question

    @staticmethod
    def delete_question(db: Session, question_id: str) -> bool:
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return False

        db.delete(db_question)
        db.commit()
        return True

    @staticmethod
    def get_answers(db: Session, question_id: str) -> List[Answer]:
        return (
            db.query(Answer)
            .filter(Answer.question_id == question_id)
            .order_by(Answer.is_accepted.desc(), Answer.vote_count.desc())
            .all()
        )

    @staticmethod
    def create_answer(
        db: Session, question_id: str, answer: AnswerCreate, user_id: str
    ) -> Optional[Answer]:
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None

        db_answer = Answer(
            question_id=question_id, user_id=user_id, content=answer.content
        )
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)
        return db_answer

    @staticmethod
    def update_answer(
        db: Session, answer_id: str, answer: AnswerUpdate
    ) -> Optional[Answer]:
        db_answer = db.query(Answer).filter(Answer.id == answer_id).first()
        if not db_answer:
            return None

        for key, value in answer.dict(exclude_unset=True).items():
            setattr(db_answer, key, value)

        db.commit()
        db.refresh(db_answer)
        return db_answer

    @staticmethod
    def delete_answer(db: Session, answer_id: str) -> bool:
        db_answer = db.query(Answer).filter(Answer.id == answer_id).first()
        if not db_answer:
            return False

        db.delete(db_answer)
        db.commit()
        return True

    @staticmethod
    def vote_answer(db: Session, answer_id: str, user_id: str, value: int) -> Optional[Answer]:
        db_answer = db.query(Answer).filter(Answer.id == answer_id).first()
        if not db_answer:
            return None

        # Check if user already voted
        db_vote = (
            db.query(AnswerVote)
            .filter(AnswerVote.answer_id == answer_id, AnswerVote.user_id == user_id)
            .first()
        )

        if db_vote:
            # Update existing vote
            if db_vote.value != value:
                db_answer.vote_count = db_answer.vote_count - db_vote.value + value
                db_vote.value = value
        else:
            # Create new vote
            db_vote = AnswerVote(answer_id=answer_id, user_id=user_id, value=value)
            db.add(db_vote)
            db_answer.vote_count += value

        db.commit()
        db.refresh(db_answer)
        return db_answer

    @staticmethod
    def accept_answer(
        db: Session, question_id: str, answer_id: str
    ) -> Optional[Question]:
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None

        db_answer = (
            db.query(Answer)
            .filter(Answer.id == answer_id, Answer.question_id == question_id)
            .first()
        )
        if not db_answer:
            return None

        # Reset previously accepted answer
        if db_question.accepted_answer_id:
            prev_answer = (
                db.query(Answer)
                .filter(Answer.id == db_question.accepted_answer_id)
                .first()
            )
            if prev_answer:
                prev_answer.is_accepted = False

        # Set new accepted answer
        db_answer.is_accepted = True
        db_question.accepted_answer_id = answer_id
        db_question.is_resolved = True
        db_question.resolved_at = datetime.now()

        db.commit()
        db.refresh(db_question)
        return db_question

    @staticmethod
    def increment_view_count(db: Session, question_id: str) -> None:
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if db_question:
            db_question.view_count += 1
            db.commit()
```

### 分類服務

```python
# services/category.py
from typing import List, Optional
from sqlalchemy.orm import Session

from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    def get_categories(db: Session) -> List[Category]:
        return db.query(Category).filter(Category.parent_id.is_(None)).order_by(Category.order).all()

    @staticmethod
    def get_category(db: Session, category_id: str) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> Category:
        db_category = Category(
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def update_category(
        db: Session, category_id: str, category: CategoryUpdate
    ) -> Optional[Category]:
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            return None

        for key, value in category.dict(exclude_unset=True).items():
            setattr(db_category, key, value)

        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete_category(db: Session, category_id: str) -> bool:
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            return False

        db.delete(db_category)
        db.commit()
        return True
```

### 搜索服務

```python
# services/search.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from models.document import Document
from models.question import Question, Answer
from schemas.search import SearchResult
from utils.search import search_documents, search_questions, search_answers


class SearchService:
    @staticmethod
    def search(
        db: Session,
        q: str,
        type: Optional[str] = None,
        category_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[SearchResult]:
        results = []

        if type in [None, "all", "document"]:
            document_results = search_documents(db, q, category_id)
            for doc in document_results:
                results.append(
                    SearchResult(
                        id=doc.id,
                        title=doc.title,
                        content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                        type="document",
                        url=f"/documents/{doc.id}",
                        highlights=[],  # Implement highlighting
                        score=1.0,  # Implement scoring
                        created_at=doc.created_at,
                        updated_at=doc.updated_at,
                    )
                )

        if type in [None, "all", "question"]:
            question_results = search_questions(db, q)
            for question in question_results:
                results.append(
                    SearchResult(
                        id=question.id,
                        title=question.title,
                        content=question.content[:200] + "..." if len(question.content) > 200 else question.content,
                        type="question",
                        url=f"/questions/{question.id}",
                        highlights=[],  # Implement highlighting
                        score=0.9,  # Implement scoring
                        created_at=question.created_at,
                        updated_at=question.updated_at,
                    )
                )

        if type in [None, "all", "answer"]:
            answer_results = search_answers(db, q)
            for answer in answer_results:
                results.append(
                    SearchResult(
                        id=answer.id,
                        title=f"Answer to: {answer.question.title}",
                        content=answer.content[:200] + "..." if len(answer.content) > 200 else answer.content,
                        type="answer",
                        url=f"/questions/{answer.question_id}#answer-{answer.id}",
                        highlights=[],  # Implement highlighting
                        score=0.8,  # Implement scoring
                        created_at=answer.created_at,
                        updated_at=answer.updated_at,
                    )
                )

        # Sort by score and apply pagination
        results.sort(key=lambda x: x.score, reverse=True)
        return results[skip : skip + limit]
```

## 主程序

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.v1 import document, question, category, search, tag, user
from core.config import settings
from db.init_db import init_db

app = FastAPI(
    title="Knowledge API",
    description="Knowledge API for internal knowledge base",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document.router, prefix="/api/v1", tags=["documents"])
app.include_router(question.router, prefix="/api/v1", tags=["questions"])
app.include_router(category.router, prefix="/api/v1", tags=["categories"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(tag.router, prefix="/api/v1", tags=["tags"])
app.include_router(user.router, prefix="/api/v1", tags=["users"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return {"message": "Welcome to Knowledge API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

## 依賴

```
# requirements.txt
fastapi==0.95.1
uvicorn==0.22.0
sqlalchemy==2.0.12
psycopg2-binary==2.9.6
pydantic==1.10.7
python-multipart==0.0.6
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.0.1
alembic==1.10.4
python-dotenv==1.0.0
tenacity==8.2.2
requests==2.29.0
pillow==9.5.0
python-slugify==8.0.1
email-validator==2.0.0.post2
pytest==7.3.1
pytest-asyncio==0.21.0
httpx==0.24.1
```