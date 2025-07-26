# Ticket 系統前端

## 概述

本目錄包含 Ticket 系統的前端代碼，使用 Vue 3 + Vite + TypeScript 開發。Ticket 系統提供工單創建、處理、簽核和追蹤功能，確保所有變更都經過適當的審核和記錄。

## 目錄結構

```
├── components/          # 組件
│   ├── common/          # 通用組件
│   ├── form/            # 表單組件
│   ├── list/            # 列表組件
│   ├── detail/          # 詳情組件
│   └── workflow/        # 工作流組件
├── views/               # 頁面
│   ├── dashboard/       # 儀表板頁面
│   ├── ticket/          # 工單頁面
│   ├── workflow/        # 工作流頁面
│   ├── report/          # 報表頁面
│   └── settings/        # 設置頁面
├── store/               # 狀態管理
│   ├── modules/         # 模塊
│   ├── actions.ts       # 操作
│   ├── mutations.ts     # 變更
│   ├── getters.ts       # 獲取器
│   └── index.ts         # 入口
├── api/                 # API 調用
│   ├── ticket.ts        # 工單 API
│   ├── workflow.ts      # 工作流 API
│   ├── user.ts          # 用戶 API
│   └── report.ts        # 報表 API
├── router/              # 路由
│   └── index.ts         # 路由配置
├── types/               # 類型定義
│   ├── ticket.ts        # 工單類型
│   ├── workflow.ts      # 工作流類型
│   ├── user.ts          # 用戶類型
│   └── report.ts        # 報表類型
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

### 工單管理

- **工單創建**：創建新工單，選擇工單類型，填寫必要信息
- **工單列表**：查看所有工單，支持篩選、排序和搜索
- **工單詳情**：查看工單詳細信息，包括歷史記錄和附件
- **工單編輯**：編輯工單信息，上傳附件

### 工作流程與簽核

- **工單處理**：處理工單，添加處理意見和附件
- **工單簽核**：審核工單，同意或拒絕
- **工作流配置**：配置工作流程和簽核規則
- **工作流可視化**：可視化展示工作流程

### 通知與提醒

- **通知中心**：查看所有通知
- **郵件通知**：接收郵件通知
- **站內消息**：接收站內消息
- **通知設置**：配置通知方式和頻率

### 報表與分析

- **工單統計**：工單數量、類型、狀態等統計
- **處理效率**：工單處理時間、處理人效率等統計
- **趨勢分析**：工單趨勢分析
- **自定義報表**：創建自定義報表

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

### 工單組件

- **TicketForm**：工單表單組件
- **TicketList**：工單列表組件
- **TicketDetail**：工單詳情組件
- **TicketHistory**：工單歷史記錄組件
- **TicketAttachment**：工單附件組件
- **TicketComment**：工單評論組件

### 工作流組件

- **WorkflowViewer**：工作流可視化組件
- **WorkflowEditor**：工作流編輯組件
- **ApprovalForm**：簽核表單組件
- **ApprovalHistory**：簽核歷史記錄組件
- **StepConfig**：步驟配置組件
- **TransitionConfig**：轉換配置組件

## 頁面設計

### 儀表板頁面

儀表板頁面顯示工單統計信息和待處理工單。

```vue
<template>
  <div class="dashboard">
    <h1>儀表板</h1>
    <div class="dashboard-stats">
      <stat-card title="待處理工單" :value="stats.pending" icon="ticket" />
      <stat-card title="今日新增" :value="stats.today" icon="plus" />
      <stat-card title="本週完成" :value="stats.completed" icon="check" />
      <stat-card title="平均處理時間" :value="stats.avgTime" icon="clock" />
    </div>
    <div class="dashboard-charts">
      <ticket-trend-chart />
      <ticket-type-chart />
    </div>
    <div class="dashboard-tables">
      <pending-ticket-table />
      <recent-activity-table />
    </div>
  </div>
</template>
```

### 工單列表頁面

工單列表頁面顯示所有工單，支持篩選、排序和搜索。

```vue
<template>
  <div class="ticket-list">
    <h1>工單列表</h1>
    <div class="ticket-list-header">
      <search-box v-model="searchQuery" placeholder="搜索工單" />
      <filter-dropdown v-model="filters" :options="filterOptions" />
      <button class="btn-primary" @click="createTicket">創建工單</button>
    </div>
    <ticket-table
      :tickets="tickets"
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
</template>
```

### 工單詳情頁面

工單詳情頁面顯示工單詳細信息，包括歷史記錄和附件。

```vue
<template>
  <div class="ticket-detail">
    <div class="ticket-detail-header">
      <h1>{{ ticket.title }}</h1>
      <div class="ticket-detail-meta">
        <span class="ticket-id">{{ ticket.id }}</span>
        <span class="ticket-status">{{ ticket.status }}</span>
        <span class="ticket-priority">{{ ticket.priority }}</span>
      </div>
      <div class="ticket-detail-actions">
        <button class="btn-primary" @click="editTicket">編輯</button>
        <button class="btn-secondary" @click="processTicket">處理</button>
      </div>
    </div>
    <div class="ticket-detail-content">
      <ticket-info :ticket="ticket" />
      <ticket-attachment :attachments="ticket.attachments" />
      <ticket-comment :comments="ticket.comments" @add="addComment" />
      <ticket-history :history="ticket.history" />
    </div>
  </div>
</template>
```

### 工單創建頁面

工單創建頁面用於創建新工單，選擇工單類型，填寫必要信息。

```vue
<template>
  <div class="ticket-create">
    <h1>創建工單</h1>
    <ticket-form
      :ticket-types="ticketTypes"
      :users="users"
      @submit="submitTicket"
      @cancel="cancelTicket"
    />
  </div>
</template>
```

### 工作流配置頁面

工作流配置頁面用於配置工作流程和簽核規則。

```vue
<template>
  <div class="workflow-config">
    <h1>工作流配置</h1>
    <div class="workflow-config-header">
      <select v-model="selectedWorkflow">
        <option v-for="wf in workflows" :key="wf.id" :value="wf.id">
          {{ wf.name }}
        </option>
      </select>
      <button class="btn-primary" @click="createWorkflow">創建工作流</button>
    </div>
    <div class="workflow-config-content">
      <workflow-editor
        :workflow="currentWorkflow"
        @save="saveWorkflow"
        @cancel="cancelWorkflow"
      />
    </div>
  </div>
</template>
```

## 狀態管理

系統使用 Pinia 進行狀態管理，按功能模塊組織 Store。

### 工單 Store

```typescript
// store/modules/ticket.ts
import { defineStore } from 'pinia'
import { Ticket, TicketType, TicketStatus } from '@/types/ticket'
import { getTickets, getTicket, createTicket, updateTicket } from '@/api/ticket'

export const useTicketStore = defineStore('ticket', {
  state: () => ({
    tickets: [] as Ticket[],
    currentTicket: null as Ticket | null,
    ticketTypes: [] as TicketType[],
    loading: false,
    error: null as string | null,
  }),
  getters: {
    pendingTickets: (state) => state.tickets.filter(t => t.status === TicketStatus.Pending),
    completedTickets: (state) => state.tickets.filter(t => t.status === TicketStatus.Completed),
    rejectedTickets: (state) => state.tickets.filter(t => t.status === TicketStatus.Rejected),
  },
  actions: {
    async fetchTickets(params: any) {
      this.loading = true
      try {
        const response = await getTickets(params)
        this.tickets = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async fetchTicket(id: string) {
      this.loading = true
      try {
        const response = await getTicket(id)
        this.currentTicket = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async submitTicket(ticket: Ticket) {
      this.loading = true
      try {
        if (ticket.id) {
          await updateTicket(ticket.id, ticket)
        } else {
          await createTicket(ticket)
        }
        await this.fetchTickets({})
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
  },
})
```

### 工作流 Store

```typescript
// store/modules/workflow.ts
import { defineStore } from 'pinia'
import { Workflow, WorkflowStep, WorkflowTransition } from '@/types/workflow'
import { getWorkflows, getWorkflow, createWorkflow, updateWorkflow } from '@/api/workflow'

export const useWorkflowStore = defineStore('workflow', {
  state: () => ({
    workflows: [] as Workflow[],
    currentWorkflow: null as Workflow | null,
    loading: false,
    error: null as string | null,
  }),
  getters: {
    activeWorkflows: (state) => state.workflows.filter(w => w.isActive),
  },
  actions: {
    async fetchWorkflows() {
      this.loading = true
      try {
        const response = await getWorkflows()
        this.workflows = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async fetchWorkflow(id: string) {
      this.loading = true
      try {
        const response = await getWorkflow(id)
        this.currentWorkflow = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    async submitWorkflow(workflow: Workflow) {
      this.loading = true
      try {
        if (workflow.id) {
          await updateWorkflow(workflow.id, workflow)
        } else {
          await createWorkflow(workflow)
        }
        await this.fetchWorkflows()
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

### 工單 API

```typescript
// api/ticket.ts
import axios from 'axios'
import { Ticket } from '@/types/ticket'

const API_URL = '/api/tickets'

export const getTickets = (params: any) => {
  return axios.get(API_URL, { params })
}

export const getTicket = (id: string) => {
  return axios.get(`${API_URL}/${id}`)
}

export const createTicket = (ticket: Ticket) => {
  return axios.post(API_URL, ticket)
}

export const updateTicket = (id: string, ticket: Ticket) => {
  return axios.put(`${API_URL}/${id}`, ticket)
}

export const deleteTicket = (id: string) => {
  return axios.delete(`${API_URL}/${id}`)
}

export const processTicket = (id: string, data: any) => {
  return axios.post(`${API_URL}/${id}/process`, data)
}

export const approveTicket = (id: string, data: any) => {
  return axios.post(`${API_URL}/${id}/approve`, data)
}

export const rejectTicket = (id: string, data: any) => {
  return axios.post(`${API_URL}/${id}/reject`, data)
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
```

### 工作流 API

```typescript
// api/workflow.ts
import axios from 'axios'
import { Workflow } from '@/types/workflow'

const API_URL = '/api/workflows'

export const getWorkflows = () => {
  return axios.get(API_URL)
}

export const getWorkflow = (id: string) => {
  return axios.get(`${API_URL}/${id}`)
}

export const createWorkflow = (workflow: Workflow) => {
  return axios.post(API_URL, workflow)
}

export const updateWorkflow = (id: string, workflow: Workflow) => {
  return axios.put(`${API_URL}/${id}`, workflow)
}

export const deleteWorkflow = (id: string) => {
  return axios.delete(`${API_URL}/${id}`)
}

export const getWorkflowSteps = (workflowId: string) => {
  return axios.get(`${API_URL}/${workflowId}/steps`)
}

export const createWorkflowStep = (workflowId: string, step: any) => {
  return axios.post(`${API_URL}/${workflowId}/steps`, step)
}

export const updateWorkflowStep = (workflowId: string, stepId: string, step: any) => {
  return axios.put(`${API_URL}/${workflowId}/steps/${stepId}`, step)
}

export const deleteWorkflowStep = (workflowId: string, stepId: string) => {
  return axios.delete(`${API_URL}/${workflowId}/steps/${stepId}`)
}

export const getWorkflowTransitions = (workflowId: string) => {
  return axios.get(`${API_URL}/${workflowId}/transitions`)
}

export const createWorkflowTransition = (workflowId: string, transition: any) => {
  return axios.post(`${API_URL}/${workflowId}/transitions`, transition)
}

export const updateWorkflowTransition = (workflowId: string, transitionId: string, transition: any) => {
  return axios.put(`${API_URL}/${workflowId}/transitions/${transitionId}`, transition)
}

export const deleteWorkflowTransition = (workflowId: string, transitionId: string) => {
  return axios.delete(`${API_URL}/${workflowId}/transitions/${transitionId}`)
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
    path: '/tickets',
    name: 'TicketList',
    component: () => import('@/views/ticket/List.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tickets/create',
    name: 'TicketCreate',
    component: () => import('@/views/ticket/Create.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tickets/:id',
    name: 'TicketDetail',
    component: () => import('@/views/ticket/Detail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tickets/:id/edit',
    name: 'TicketEdit',
    component: () => import('@/views/ticket/Edit.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/workflows',
    name: 'WorkflowList',
    component: () => import('@/views/workflow/List.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/workflows/create',
    name: 'WorkflowCreate',
    component: () => import('@/views/workflow/Create.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/workflows/:id',
    name: 'WorkflowDetail',
    component: () => import('@/views/workflow/Detail.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/workflows/:id/edit',
    name: 'WorkflowEdit',
    component: () => import('@/views/workflow/Edit.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/reports',
    name: 'ReportList',
    component: () => import('@/views/report/List.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/reports/:id',
    name: 'ReportDetail',
    component: () => import('@/views/report/Detail.vue'),
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
// types/ticket.ts
export enum TicketStatus {
  Pending = 'pending',
  Processing = 'processing',
  Approving = 'approving',
  Completed = 'completed',
  Rejected = 'rejected',
}

export enum TicketPriority {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
  Urgent = 'urgent',
}

export interface Ticket {
  id?: string
  title: string
  description: string
  ticketTypeId: string
  workflowId: string
  creatorId: string
  assigneeId?: string
  status: TicketStatus
  priority: TicketPriority
  createdAt?: string
  updatedAt?: string
  dueDate?: string
  attachments?: TicketAttachment[]
  comments?: TicketComment[]
  history?: TicketHistory[]
}

export interface TicketType {
  id: string
  name: string
  description: string
  isActive: boolean
  fieldsConfig: any
  createdAt: string
  updatedAt: string
}

export interface TicketAttachment {
  id: string
  ticketId: string
  userId: string
  filename: string
  filePath: string
  fileType: string
  fileSize: number
  createdAt: string
}

export interface TicketComment {
  id: string
  ticketId: string
  userId: string
  content: string
  createdAt: string
  updatedAt: string
}

export interface TicketHistory {
  id: string
  ticketId: string
  userId: string
  action: string
  changes: any
  createdAt: string
}
```

```typescript
// types/workflow.ts
export interface Workflow {
  id: string
  name: string
  description: string
  ticketTypeId: string
  isActive: boolean
  createdAt: string
  updatedAt: string
  steps?: WorkflowStep[]
  transitions?: WorkflowTransition[]
}

export interface WorkflowStep {
  id: string
  workflowId: string
  name: string
  description: string
  order: number
  isInitial: boolean
  isFinal: boolean
  createdAt: string
  updatedAt: string
}

export interface WorkflowTransition {
  id: string
  fromStepId: string
  toStepId: string
  name: string
  description: string
  conditions: any
  createdAt: string
  updatedAt: string
}

export interface ApprovalRule {
  id: string
  workflowStepId: string
  ruleType: string
  ruleConfig: any
  createdAt: string
  updatedAt: string
}
```

```typescript
// types/user.ts
export interface User {
  id: string
  username: string
  email: string
  fullName: string
  department: string
  isActive: boolean
  createdAt: string
  updatedAt: string
  roles?: Role[]
}

export interface Role {
  id: string
  name: string
  description: string
  permissions: any
  createdAt: string
  updatedAt: string
}
```