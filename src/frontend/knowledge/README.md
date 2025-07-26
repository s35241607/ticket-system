# Knowledge 系統前端

## 概述

本目錄包含 Knowledge 系統的前端代碼，使用 Vue 3 + Vite + TypeScript 開發。Knowledge 系統用於維護內部知識庫，包括系統操作指南、問答集和異常處理流程，幫助員工快速獲取所需信息和解決問題。

## 目錄結構

```
├── components/          # 組件
│   ├── common/          # 通用組件
│   ├── document/        # 文檔組件
│   ├── search/          # 搜索組件
│   ├── question/        # 問答組件
│   └── category/        # 分類組件
├── views/               # 頁面
│   ├── dashboard/       # 儀表板頁面
│   ├── document/        # 文檔頁面
│   ├── question/        # 問答頁面
│   ├── search/          # 搜索頁面
│   └── settings/        # 設置頁面
├── store/               # 狀態管理
│   ├── modules/         # 模塊
│   ├── actions.ts       # 操作
│   ├── mutations.ts     # 變更
│   ├── getters.ts       # 獲取器
│   └── index.ts         # 入口
├── api/                 # API 調用
│   ├── document.ts      # 文檔 API
│   ├── question.ts      # 問答 API
│   ├── category.ts      # 分類 API
│   └── search.ts        # 搜索 API
├── router/              # 路由
│   └── index.ts         # 路由配置
├── types/               # 類型定義
│   ├── document.ts      # 文檔類型
│   ├── question.ts      # 問答類型
│   ├── category.ts      # 分類類型
│   └── search.ts        # 搜索類型
├── utils/               # 工具函數
│   ├── format.ts        # 格式化工具
│   ├── validation.ts    # 驗證工具
│   └── auth.ts          # 認證工具
└── assets/              # 靜態資源
    ├── images/          # 圖片
    ├── styles/          # 樣式
    └── icons/           # 圖標
```

## 主要功能

### 知識文檔管理

- **文檔創建**：創建新文檔，選擇分類，填寫內容
- **文檔列表**：查看所有文檔，支持篩選、排序和搜索
- **文檔詳情**：查看文檔詳細內容，包括附件和評論
- **文檔編輯**：編輯文檔內容，上傳附件

### 問答功能

- **問題提出**：提出新問題
- **問題列表**：查看所有問題，支持篩選、排序和搜索
- **問題詳情**：查看問題詳細內容，包括回答
- **回答問題**：回答問題，評價回答

### 全文搜索

- **簡單搜索**：快速搜索知識內容
- **高級搜索**：使用高級選項精確搜索
- **搜索結果**：顯示搜索結果，支持篩選和排序
- **相關推薦**：推薦相關內容

### 知識分類與標籤

- **分類管理**：管理知識分類
- **標籤管理**：管理知識標籤
- **分類瀏覽**：按分類瀏覽知識
- **標籤瀏覽**：按標籤瀏覽知識

## 組件設計

### 通用組件

- **Header**：頁面頭部，包含導航和用戶信息
- **Sidebar**：側邊欄，包含菜單
- **Footer**：頁面底部，包含版權信息
- **Breadcrumb**：麵包屑導航
- **Pagination**：分頁組件
- **Search**：搜索組件
- **Filter**：篩選組件
- **Table**：表格組件
- **Modal**：模態框組件
- **Notification**：通知組件

### 文檔組件

- **DocumentForm**：文檔表單組件
- **DocumentList**：文檔列表組件
- **DocumentDetail**：文檔詳情組件
- **DocumentHistory**：文檔歷史記錄組件
- **DocumentAttachment**：文檔附件組件
- **DocumentComment**：文檔評論組件
- **MarkdownEditor**：Markdown 編輯器組件
- **MarkdownViewer**：Markdown 查看器組件

### 問答組件

- **QuestionForm**：問題表單組件
- **QuestionList**：問題列表組件
- **QuestionDetail**：問題詳情組件
- **AnswerForm**：回答表單組件
- **AnswerList**：回答列表組件
- **AnswerDetail**：回答詳情組件
- **VoteButton**：投票按鈕組件

### 分類組件

- **CategoryTree**：分類樹組件
- **CategoryForm**：分類表單組件
- **TagCloud**：標籤雲組件
- **TagForm**：標籤表單組件

## 頁面設計

### 儀表板頁面

儀表板頁面顯示知識統計信息和熱門內容。

```vue
<template>
  <div class="dashboard">
    <h1>儀表板</h1>
    <div class="dashboard-stats">
      <stat-card title="知識文檔" :value="stats.documents" icon="document" />
      <stat-card title="問答數量" :value="stats.questions" icon="question" />
      <stat-card title="今日訪問" :value="stats.visits" icon="eye" />
      <stat-card title="解決問題" :value="stats.solved" icon="check" />
    </div>
    <div class="dashboard-charts">
      <document-trend-chart />
      <category-distribution-chart />
    </div>
    <div class="dashboard-tables">
      <popular-document-table />
      <recent-question-table />
    </div>
  </div>
</template>
```

### 文檔列表頁面

文檔列表頁面顯示所有文檔，支持篩選、排序和搜索。

```vue
<template>
  <div class="document-list">
    <h1>知識文檔</h1>
    <div class="document-list-header">
      <search-box v-model="searchQuery" placeholder="搜索文檔" />
      <filter-dropdown v-model="filters" :options="filterOptions" />
      <button class="btn-primary" @click="createDocument">創建文檔</button>
    </div>
    <div class="document-list-content">
      <div class="document-list-sidebar">
        <category-tree
          :categories="categories"
          :selected="selectedCategory"
          @select="selectCategory"
        />
      </div>
      <div class="document-list-main">
        <document-table
          :documents="documents"
          :loading="loading"
          @sort="handleSort"
          @page="handlePage"
        />
        <pagination
          :total="total"
          :current="page"
          :size="pageSize"
          @change="handlePage"
        />
      </div>
    </div>
  </div>
</template>
```

### 文檔詳情頁面

文檔詳情頁面顯示文檔詳細內容，包括附件和評論。

```vue
<template>
  <div class="document-detail">
    <div class="document-detail-header">
      <h1>{{ document.title }}</h1>
      <div class="document-detail-meta">
        <span class="document-category">{{ document.category.name }}</span>
        <span class="document-author">{{ document.creator.fullName }}</span>
        <span class="document-date">{{ formatDate(document.updatedAt) }}</span>
        <span class="document-views">{{ document.viewCount }} 次查看</span>
      </div>
      <div class="document-detail-actions">
        <button class="btn-primary" @click="editDocument">編輯</button>
        <button class="btn-secondary" @click="downloadDocument">下載</button>
      </div>
    </div>
    <div class="document-detail-content">
      <markdown-viewer :content="document.content" />
      <document-attachment :attachments="document.attachments" />
      <document-comment
        :comments="document.comments"
        @add="addComment"
      />
    </div>
    <div class="document-detail-sidebar">
      <div class="document-detail-toc">
        <h3>目錄</h3>
        <document-toc :content="document.content" />
      </div>
      <div class="document-detail-related">
        <h3>相關文檔</h3>
        <related-document-list :documents="relatedDocuments" />
      </div>
    </div>
  </div>
</template>
```

### 文檔創建頁面

文檔創建頁面用於創建新文檔，選擇分類，填寫內容。

```vue
<template>
  <div class="document-create">
    <h1>創建文檔</h1>
    <document-form
      :categories="categories"
      :tags="tags"
      @submit="submitDocument"
      @cancel="cancelDocument"
    >
      <template #editor>
        <markdown-editor v-model="document.content" />
      </template>
    </document-form>
  </div>
</template>
```

### 問答列表頁面

問答列表頁面顯示所有問題，支持篩選、排序和搜索。

```vue
<template>
  <div class="question-list">
    <h1>問答中心</h1>
    <div class="question-list-header">
      <search-box v-model="searchQuery" placeholder="搜索問題" />
      <filter-dropdown v-model="filters" :options="filterOptions" />
      <button class="btn-primary" @click="createQuestion">提問</button>
    </div>
    <div class="question-list-content">
      <div class="question-list-main">
        <question-table
          :questions="questions"
          :loading="loading"
          @sort="handleSort"
          @page="handlePage"
        />
        <pagination
          :total="total"
          :current="page"
          :size="pageSize"
          @change="handlePage"
        />
      </div>
      <div class="question-list-sidebar">
        <div class="question-list-stats">
          <h3>統計</h3>
          <stat-card title="總問題" :value="stats.total" />
          <stat-card title="已解決" :value="stats.solved" />
          <stat-card title="待解決" :value="stats.unsolved" />
        </div>
        <div class="question-list-tags">
          <h3>熱門標籤</h3>
          <tag-cloud :tags="popularTags" @select="selectTag" />
        </div>
      </div>
    </div>
  </div>
</template>
```

### 問題詳情頁面

問題詳情頁面顯示問題詳細內容，包括回答。

```vue
<template>
  <div class="question-detail">
    <div class="question-detail-header">
      <h1>{{ question.title }}</h1>
      <div class="question-detail-meta">
        <span class="question-author">{{ question.user.fullName }}</span>
        <span class="question-date">{{ formatDate(question.createdAt) }}</span>
        <span class="question-views">{{ question.viewCount }} 次查看</span>
        <span
          class="question-status"
          :class="{ 'is-resolved': question.isResolved }"
        >
          {{ question.isResolved ? '已解決' : '待解決' }}
        </span>
      </div>
    </div>
    <div class="question-detail-content">
      <markdown-viewer :content="question.content" />
    </div>
    <div class="question-detail-answers">
      <h2>{{ answers.length }} 個回答</h2>
      <answer-list
        :answers="answers"
        :accepted-answer-id="question.acceptedAnswerId"
        @vote="handleVote"
        @accept="handleAccept"
      />
    </div>
    <div class="question-detail-your-answer">
      <h2>你的回答</h2>
      <answer-form @submit="submitAnswer" />
    </div>
    <div class="question-detail-sidebar">
      <div class="question-detail-related">
        <h3>相關問題</h3>
        <related-question-list :questions="relatedQuestions" />
      </div>
      <div class="question-detail-related-docs">
        <h3>相關文檔</h3>
        <related-document-list :documents="relatedDocuments" />
      </div>
    </div>
  </div>
</template>
```

## 狀態管理

系統使用 Pinia 進行狀態管理，按功能模塊組織 Store。

### 文檔 Store

```typescript
// store/modules/document.ts
import { defineStore } from 'pinia'
import { Document, DocumentCategory } from '@/types/document'
import {
  getDocuments,
  getDocument,
  createDocument,
  updateDocument,
} from '@/api/document'

export const useDocumentStore = defineStore('document', {
  state: () => ({
    documents: [] as Document[],
    currentDocument: null as Document | null,
    categories: [] as DocumentCategory[],
    loading: false,
    error: null as string | null,
  }),
  getters: {
    publishedDocuments: (state) =>
      state.documents.filter((d) => d.isPublished),
    documentsByCategory: (state) => (categoryId: string) =>
      state.documents.filter((d) => d.categoryId === categoryId),
  },
  actions: {
    async fetchDocuments(params: any) {
      this.loading = true
      try {
        const response = await getDocuments(params)
        this.documents = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async fetchDocument(id: string) {
      this.loading = true
      try {
        const response = await getDocument(id)
        this.currentDocument = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async submitDocument(document: Document) {
      this.loading = true
      try {
        if (document.id) {
          await updateDocument(document.id, document)
        } else {
          await createDocument(document)
        }
        await this.fetchDocuments({})
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
  },
})
```

### 問答 Store

```typescript
// store/modules/question.ts
import { defineStore } from 'pinia'
import { Question, Answer } from '@/types/question'
import {
  getQuestions,
  getQuestion,
  createQuestion,
  updateQuestion,
  getAnswers,
  createAnswer,
  updateAnswer,
  voteAnswer,
  acceptAnswer,
} from '@/api/question'

export const useQuestionStore = defineStore('question', {
  state: () => ({
    questions: [] as Question[],
    currentQuestion: null as Question | null,
    answers: [] as Answer[],
    loading: false,
    error: null as string | null,
  }),
  getters: {
    resolvedQuestions: (state) =>
      state.questions.filter((q) => q.isResolved),
    unresolvedQuestions: (state) =>
      state.questions.filter((q) => !q.isResolved),
  },
  actions: {
    async fetchQuestions(params: any) {
      this.loading = true
      try {
        const response = await getQuestions(params)
        this.questions = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async fetchQuestion(id: string) {
      this.loading = true
      try {
        const response = await getQuestion(id)
        this.currentQuestion = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async fetchAnswers(questionId: string) {
      this.loading = true
      try {
        const response = await getAnswers(questionId)
        this.answers = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async submitQuestion(question: Question) {
      this.loading = true
      try {
        if (question.id) {
          await updateQuestion(question.id, question)
        } else {
          await createQuestion(question)
        }
        await this.fetchQuestions({})
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async submitAnswer(questionId: string, answer: Answer) {
      this.loading = true
      try {
        if (answer.id) {
          await updateAnswer(answer.id, answer)
        } else {
          await createAnswer(questionId, answer)
        }
        await this.fetchAnswers(questionId)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async voteForAnswer(answerId: string, value: number) {
      this.loading = true
      try {
        await voteAnswer(answerId, value)
        if (this.currentQuestion) {
          await this.fetchAnswers(this.currentQuestion.id)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async acceptTheAnswer(questionId: string, answerId: string) {
      this.loading = true
      try {
        await acceptAnswer(questionId, answerId)
        await this.fetchQuestion(questionId)
        await this.fetchAnswers(questionId)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
  },
})
```

## API 調用

系統使用 Axios 進行 API 調用，API 調用封裝在專門的服務中。

### 文檔 API

```typescript
// api/document.ts
import axios from 'axios'
import { Document } from '@/types/document'

const API_URL = '/api/documents'

export const getDocuments = (params: any) => {
  return axios.get(API_URL, { params })
}

export const getDocument = (id: string) => {
  return axios.get(`${API_URL}/${id}`)
}

export const createDocument = (document: Document) => {
  return axios.post(API_URL, document)
}

export const updateDocument = (id: string, document: Document) => {
  return axios.put(`${API_URL}/${id}`, document)
}

export const deleteDocument = (id: string) => {
  return axios.delete(`${API_URL}/${id}`)
}

export const uploadAttachment = (id: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post(`${API_URL}/${id}/attachments`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export const addComment = (id: string, comment: string) => {
  return axios.post(`${API_URL}/${id}/comments`, { content: comment })
}

export const getDocumentHistory = (id: string) => {
  return axios.get(`${API_URL}/${id}/history`)
}

export const getRelatedDocuments = (id: string) => {
  return axios.get(`${API_URL}/${id}/related`)
}
```

### 問答 API

```typescript
// api/question.ts
import axios from 'axios'
import { Question, Answer } from '@/types/question'

const API_URL = '/api/questions'

export const getQuestions = (params: any) => {
  return axios.get(API_URL, { params })
}

export const getQuestion = (id: string) => {
  return axios.get(`${API_URL}/${id}`)
}

export const createQuestion = (question: Question) => {
  return axios.post(API_URL, question)
}

export const updateQuestion = (id: string, question: Question) => {
  return axios.put(`${API_URL}/${id}`, question)
}

export const deleteQuestion = (id: string) => {
  return axios.delete(`${API_URL}/${id}`)
}

export const getAnswers = (questionId: string) => {
  return axios.get(`${API_URL}/${questionId}/answers`)
}

export const getAnswer = (questionId: string, answerId: string) => {
  return axios.get(`${API_URL}/${questionId}/answers/${answerId}`)
}

export const createAnswer = (questionId: string, answer: Answer) => {
  return axios.post(`${API_URL}/${questionId}/answers`, answer)
}

export const updateAnswer = (answerId: string, answer: Answer) => {
  return axios.put(`/api/answers/${answerId}`, answer)
}

export const deleteAnswer = (answerId: string) => {
  return axios.delete(`/api/answers/${answerId}`)
}

export const voteAnswer = (answerId: string, value: number) => {
  return axios.post(`/api/answers/${answerId}/vote`, { value })
}

export const acceptAnswer = (questionId: string, answerId: string) => {
  return axios.post(`${API_URL}/${questionId}/accept`, { answerId })
}

export const getRelatedQuestions = (id: string) => {
  return axios.get(`${API_URL}/${id}/related`)
}
```

### 分類 API

```typescript
// api/category.ts
import axios from 'axios'
import { DocumentCategory } from '@/types/document'

const API_URL = '/api/categories'

export const getCategories = () => {
  return axios.get(API_URL)
}

export const getCategory = (id: string) => {
  return axios.get(`${API_URL}/${id}`)
}

export const createCategory = (category: DocumentCategory) => {
  return axios.post(API_URL, category)
}

export const updateCategory = (id: string, category: DocumentCategory) => {
  return axios.put(`${API_URL}/${id}`, category)
}

export const deleteCategory = (id: string) => {
  return axios.delete(`${API_URL}/${id}`)
}

export const getCategoryDocuments = (id: string) => {
  return axios.get(`${API_URL}/${id}/documents`)
}
```

### 搜索 API

```typescript
// api/search.ts
import axios from 'axios'

const API_URL = '/api/search'

export const search = (query: string, params: any = {}) => {
  return axios.get(API_URL, { params: { query, ...params } })
}

export const searchDocuments = (query: string, params: any = {}) => {
  return axios.get(`${API_URL}/documents`, { params: { query, ...params } })
}

export const searchQuestions = (query: string, params: any = {}) => {
  return axios.get(`${API_URL}/questions`, { params: { query, ...params } })
}

export const getPopularSearches = () => {
  return axios.get(`${API_URL}/popular`)
}
```

## 路由配置

系統使用 Vue Router 進行路由配置。

```typescript
// router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/Index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documents',
    name: 'DocumentList',
    component: () => import('@/views/document/List.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documents/create',
    name: 'DocumentCreate',
    component: () => import('@/views/document/Create.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documents/:id',
    name: 'DocumentDetail',
    component: () => import('@/views/document/Detail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documents/:id/edit',
    name: 'DocumentEdit',
    component: () => import('@/views/document/Edit.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documents/:id/history',
    name: 'DocumentHistory',
    component: () => import('@/views/document/History.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/categories',
    name: 'CategoryList',
    component: () => import('@/views/category/List.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/categories/:id',
    name: 'CategoryDetail',
    component: () => import('@/views/category/Detail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/questions',
    name: 'QuestionList',
    component: () => import('@/views/question/List.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/questions/create',
    name: 'QuestionCreate',
    component: () => import('@/views/question/Create.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/questions/:id',
    name: 'QuestionDetail',
    component: () => import('@/views/question/Detail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/questions/:id/edit',
    name: 'QuestionEdit',
    component: () => import('@/views/question/Edit.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/search/Index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/settings/Index.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const isAuthenticated = localStorage.getItem('token')
  const isAdmin = localStorage.getItem('isAdmin') === 'true'

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (requiresAdmin && !isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
```

## 類型定義

系統使用 TypeScript 進行類型定義。

```typescript
// types/document.ts
export interface Document {
  id?: string
  title: string
  content: string
  categoryId: string
  creatorId: string
  isPublished: boolean
  viewCount?: number
  rating?: number
  createdAt?: string
  updatedAt?: string
  publishedAt?: string
  attachments?: DocumentAttachment[]
  comments?: DocumentComment[]
  history?: DocumentHistory[]
  category?: DocumentCategory
  creator?: User
  tags?: DocumentTag[]
}

export interface DocumentCategory {
  id: string
  name: string
  description: string
  parentId?: string
  order: number
  createdAt: string
  updatedAt: string
  children?: DocumentCategory[]
}

export interface DocumentTag {
  id: string
  documentId: string
  name: string
  createdAt: string
}

export interface DocumentAttachment {
  id: string
  documentId: string
  userId: string
  filename: string
  filePath: string
  fileType: string
  fileSize: number
  createdAt: string
}

export interface DocumentComment {
  id: string
  documentId: string
  userId: string
  content: string
  createdAt: string
  updatedAt: string
}

export interface DocumentHistory {
  id: string
  documentId: string
  userId: string
  content: string
  changes: any
  createdAt: string
}
```

```typescript
// types/question.ts
export interface Question {
  id?: string
  title: string
  content: string
  userId: string
  viewCount?: number
  isResolved: boolean
  createdAt?: string
  updatedAt?: string
  resolvedAt?: string
  acceptedAnswerId?: string
  user?: User
  answers?: Answer[]
}

export interface Answer {
  id?: string
  questionId: string
  userId: string
  content: string
  isAccepted: boolean
  voteCount: number
  createdAt?: string
  updatedAt?: string
  user?: User
}

export interface User {
  id: string
  username: string
  email: string
  fullName: string
  department: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}
```

```typescript
// types/search.ts
export interface SearchResult {
  id: string
  title: string
  content: string
  type: 'document' | 'question' | 'answer'
  url: string
  highlights: string[]
  score: number
  createdAt: string
  updatedAt: string
}

export interface SearchParams {
  query: string
  type?: 'document' | 'question' | 'answer' | 'all'
  categoryId?: string
  from?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}
```