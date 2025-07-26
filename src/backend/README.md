# Ticket 與 Knowledge 系統後端

## 概述

本目錄包含 Ticket 與 Knowledge 系統的後端代碼，使用 Python FastAPI 開發。系統採用微服務架構，分為 Ticket API 和 Knowledge API 兩個主要服務。

## 目錄結構

```
├── ticket_api/           # 工單系統 API
│   ├── app/              # 應用代碼
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心功能
│   │   ├── models/       # 數據模型
│   │   ├── schemas/      # Pydantic 模型
│   │   └── services/     # 業務邏輯
│   ├── tests/            # 單元測試
│   └── alembic/          # 數據庫遷移
├── knowledge_api/        # 知識庫系統 API
│   ├── app/              # 應用代碼
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心功能
│   │   ├── models/       # 數據模型
│   │   ├── schemas/      # Pydantic 模型
│   │   └── services/     # 業務邏輯
│   ├── tests/            # 單元測試
│   └── alembic/          # 數據庫遷移
└── shared/               # 共享模組
    ├── auth/             # 認證相關
    ├── database/         # 數據庫連接
    ├── cache/            # 緩存
    ├── messaging/        # 消息隊列
    └── utils/            # 工具函數
```

## 技術棧

- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **數據庫**: PostgreSQL
- **遷移**: Alembic
- **緩存**: Redis
- **消息隊列**: Kafka
- **搜索引擎**: Elasticsearch
- **對象存儲**: MinIO
- **認證**: JWT, OAuth2
- **測試**: Pytest
- **文檔**: Swagger UI, ReDoc

## 開發指南

### 環境要求

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Kafka 2.8+
- Elasticsearch 7.10+

### 虛擬環境設置

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 運行開發服務器

```bash
cd ticket_api
uvicorn app.main:app --reload --port 8000

# 在另一個終端
cd knowledge_api
uvicorn app.main:app --reload --port 8001
```

### 數據庫遷移

```bash
cd ticket_api
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 運行測試

```bash
pytest
```

## 開發規範

### 代碼風格

- 使用 Black 和 isort 進行代碼格式化
- 使用 Flake8 進行代碼質量檢查
- 遵循 PEP 8 風格指南
- 使用類型註解確保類型安全

### API 設計

- 遵循 RESTful API 設計原則
- 使用 Pydantic 模型進行數據驗證
- 使用依賴注入進行認證和授權
- 提供詳細的 API 文檔

### 數據庫操作

- 使用 SQLAlchemy ORM 進行數據庫操作
- 使用 Alembic 進行數據庫遷移
- 避免在請求處理中進行複雜的數據庫操作
- 使用事務確保數據一致性

### 錯誤處理

- 使用 FastAPI 的異常處理機制
- 返回標準化的錯誤響應
- 記錄詳細的錯誤日誌

## 主要功能

### Ticket API

- 工單創建與提交
- 工單處理與簽核
- 工單狀態追蹤
- 通知與提醒
- 報表與分析

### Knowledge API

- 知識文檔管理
- 問答功能
- 全文搜索
- 異常處理指南
- 知識分類與標籤