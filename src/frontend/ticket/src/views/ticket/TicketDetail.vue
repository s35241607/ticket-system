<template>
  <div class="ticket-detail">
    <div class="page-header">
      <h2>工單詳情 - {{ ticket.id }}</h2>
      <div>
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" v-if="ticket.status === 'pending'">
          編輯工單
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card title="基本信息">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="工單編號">{{ ticket.id }}</el-descriptions-item>
            <el-descriptions-item label="工單標題">{{ ticket.title }}</el-descriptions-item>
            <el-descriptions-item label="工單類型">{{ ticket.type }}</el-descriptions-item>
            <el-descriptions-item label="優先級">
              <el-tag :type="getPriorityType(ticket.priority)">{{ ticket.priority }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="當前狀態">
              <el-tag :type="getStatusType(ticket.status)">{{ getStatusText(ticket.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="創建者">{{ ticket.creator }}</el-descriptions-item>
            <el-descriptions-item label="處理人">{{ ticket.assignee || '未分配' }}</el-descriptions-item>
            <el-descriptions-item label="創建時間">{{ ticket.created_at }}</el-descriptions-item>
            <el-descriptions-item label="預期完成時間">{{ ticket.expected_completion || '未設定' }}</el-descriptions-item>
            <el-descriptions-item label="實際完成時間">{{ ticket.completed_at || '未完成' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>工單描述</span>
          </template>
          <div class="description">
            {{ ticket.description }}
          </div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>處理記錄</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="record in processRecords"
              :key="record.id"
              :timestamp="record.timestamp"
              :type="record.type"
            >
              <div class="record-content">
                <div class="record-action">{{ record.action }}</div>
                <div class="record-operator">操作人：{{ record.operator }}</div>
                <div class="record-comment" v-if="record.comment">
                  備註：{{ record.comment }}
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>操作面板</span>
          </template>
          <div class="action-panel">
            <el-button type="success" style="width: 100%; margin-bottom: 10px;" v-if="ticket.status === 'pending'">
              批准工單
            </el-button>
            <el-button type="danger" style="width: 100%; margin-bottom: 10px;" v-if="ticket.status === 'pending'">
              拒絕工單
            </el-button>
            <el-button type="warning" style="width: 100%; margin-bottom: 10px;" v-if="ticket.status === 'pending'">
              要求修改
            </el-button>
            <el-button type="primary" style="width: 100%; margin-bottom: 10px;" v-if="ticket.status === 'approved'">
              開始處理
            </el-button>
            <el-button type="success" style="width: 100%; margin-bottom: 10px;" v-if="ticket.status === 'in_progress'">
              完成工單
            </el-button>
          </div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>附件</span>
          </template>
          <div class="attachments">
            <div v-if="ticket.attachments && ticket.attachments.length > 0">
              <div
                v-for="file in ticket.attachments"
                :key="file.id"
                class="attachment-item"
              >
                <el-icon><Document /></el-icon>
                <span>{{ file.name }}</span>
                <el-button type="primary" link size="small">下載</el-button>
              </div>
            </div>
            <div v-else class="no-attachments">
              暫無附件
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const ticketId = route.params.id as string

const ticket = ref({
  id: 'T001',
  title: '系統部署申請',
  type: '部署申請',
  priority: '高',
  status: 'pending',
  creator: '張三',
  assignee: '李四',
  created_at: '2025-01-26 10:30:00',
  expected_completion: '2025-01-28 18:00:00',
  completed_at: null,
  description: '需要將新版本的系統部署到生產環境，包括數據庫遷移和配置更新。請確保在部署前進行充分的測試，並準備回滾方案。',
  attachments: [
    { id: 1, name: '部署文檔.pdf' },
    { id: 2, name: '配置文件.zip' }
  ]
})

const processRecords = ref([
  {
    id: 1,
    action: '工單已創建',
    operator: '張三',
    timestamp: '2025-01-26 10:30:00',
    type: 'primary',
    comment: '初始創建工單'
  },
  {
    id: 2,
    action: '工單已分配',
    operator: '系統管理員',
    timestamp: '2025-01-26 10:35:00',
    type: 'success',
    comment: '已分配給李四處理'
  }
])

const getPriorityType = (priority: string) => {
  switch (priority) {
    case '高':
      return 'danger'
    case '中':
      return 'warning'
    case '低':
      return 'info'
    default:
      return 'info'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'pending':
      return 'warning'
    case 'in_progress':
      return 'primary'
    case 'completed':
      return 'success'
    case 'rejected':
      return 'danger'
    default:
      return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending':
      return '待審核'
    case 'in_progress':
      return '進行中'
    case 'completed':
      return '已完成'
    case 'rejected':
      return '已拒絕'
    default:
      return status
  }
}

onMounted(() => {
  // 根據 ticketId 載入工單詳情
  console.log('Loading ticket:', ticketId)
})
</script>

<style scoped>
.ticket-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.description {
  line-height: 1.6;
  color: #666;
}

.record-content {
  padding: 10px 0;
}

.record-action {
  font-weight: bold;
  margin-bottom: 5px;
}

.record-operator {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}

.record-comment {
  font-size: 14px;
  color: #666;
}

.action-panel {
  display: flex;
  flex-direction: column;
}

.attachments {
  max-height: 200px;
  overflow-y: auto;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.attachment-item:last-child {
  border-bottom: none;
}

.attachment-item .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.attachment-item span {
  flex: 1;
  margin-right: 8px;
}

.no-attachments {
  text-align: center;
  color: #999;
  padding: 20px 0;
}
</style>