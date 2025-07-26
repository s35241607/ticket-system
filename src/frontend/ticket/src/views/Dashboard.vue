<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalTickets }}</div>
            <div class="stat-label">總工單數</div>
          </div>
          <el-icon class="stat-icon"><Tickets /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.pendingTickets }}</div>
            <div class="stat-label">待處理工單</div>
          </div>
          <el-icon class="stat-icon"><Clock /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.completedTickets }}</div>
            <div class="stat-label">已完成工單</div>
          </div>
          <el-icon class="stat-icon"><Check /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.rejectedTickets }}</div>
            <div class="stat-label">已拒絕工單</div>
          </div>
          <el-icon class="stat-icon"><Close /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近工單</span>
          </template>
          <el-table :data="recentTickets" style="width: 100%">
            <el-table-column prop="id" label="工單號" width="100" />
            <el-table-column prop="title" label="標題" />
            <el-table-column prop="status" label="狀態" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="創建時間" width="150" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/tickets/create')">
              <el-icon><Plus /></el-icon>
              創建工單
            </el-button>
            <el-button @click="$router.push('/tickets')">
              <el-icon><List /></el-icon>
              查看所有工單
            </el-button>
            <el-button @click="$router.push('/workflows')">
              <el-icon><Connection /></el-icon>
              工作流程管理
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const stats = ref({
  totalTickets: 156,
  pendingTickets: 23,
  completedTickets: 128,
  rejectedTickets: 5
})

const recentTickets = ref([
  {
    id: 'T001',
    title: '系統部署申請',
    status: '待審核',
    created_at: '2025-01-26'
  },
  {
    id: 'T002',
    title: '數據庫參數調整',
    status: '進行中',
    created_at: '2025-01-25'
  },
  {
    id: 'T003',
    title: '用戶權限修改',
    status: '已完成',
    created_at: '2025-01-24'
  }
])

const getStatusType = (status: string) => {
  switch (status) {
    case '待審核':
      return 'warning'
    case '進行中':
      return 'primary'
    case '已完成':
      return 'success'
    case '已拒絕':
      return 'danger'
    default:
      return 'info'
  }
}

onMounted(() => {
  // 這裡可以調用 API 獲取實際數據
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  position: relative;
  z-index: 2;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 3rem;
  color: #409eff;
  opacity: 0.3;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-actions .el-button {
  justify-content: flex-start;
}
</style>