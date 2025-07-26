# Ticket 與 Knowledge 系統前端

## 概述

本目錄包含 Ticket 與 Knowledge 系統的前端代碼，使用 Vue 3 + Vite + TypeScript 開發。

## 目錄結構

```
├── ticket/           # 工單系統前端
│   ├── components/   # 工單系統組件
│   ├── views/        # 工單系統頁面
│   ├── store/        # 工單系統狀態管理
│   └── api/          # 工單系統 API 調用
├── knowledge/        # 知識庫系統前端
│   ├── components/   # 知識庫系統組件
│   ├── views/        # 知識庫系統頁面
│   ├── store/        # 知識庫系統狀態管理
│   └── api/          # 知識庫系統 API 調用
└── shared/           # 共享組件和功能
    ├── components/   # 共享組件
    ├── utils/        # 工具函數
    ├── styles/       # 共享樣式
    └── api/          # 共享 API 調用
```

## 技術棧

- **框架**: Vue 3
- **構建工具**: Vite
- **語言**: TypeScript
- **UI 組件庫**: Element Plus
- **狀態管理**: Pinia
- **路由**: Vue Router
- **HTTP 客戶端**: Axios
- **表單驗證**: Vee-Validate
- **圖表**: ECharts
- **編輯器**: TinyMCE / Monaco Editor
- **國際化**: Vue I18n

## 開發指南

### 環境要求

- Node.js 16+
- npm 7+ 或 yarn 1.22+

### 安裝依賴

```bash
npm install
# 或
yarn install
```

### 開發模式

```bash
npm run dev
# 或
yarn dev
```

### 構建生產版本

```bash
npm run build
# 或
yarn build
```

## 開發規範

### 代碼風格

- 使用 ESLint 和 Prettier 進行代碼格式化
- 遵循 Vue 3 組合式 API 的最佳實踐
- 使用 TypeScript 類型定義確保類型安全

### 組件開發

- 組件應該是可重用的，並且有明確的職責
- 使用 Props 和 Emits 進行組件通信
- 複雜的組件應該有單元測試

### 狀態管理

- 使用 Pinia 進行狀態管理
- 按功能模塊組織 Store
- 避免在組件中直接修改 Store 狀態

### API 調用

- 使用 Axios 進行 API 調用
- API 調用應該封裝在專門的服務中
- 使用攔截器處理通用邏輯（如錯誤處理、認證等）

## 主要功能

### Ticket 系統

- 工單創建與提交
- 工單處理與簽核
- 工單狀態追蹤
- 通知與提醒
- 報表與分析

### Knowledge 系統

- 知識文檔管理
- 問答功能
- 全文搜索
- 異常處理指南
- 知識分類與標籤