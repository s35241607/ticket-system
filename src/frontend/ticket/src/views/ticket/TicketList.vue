<template>
  <div class="ticket-list">
    <div class="page-header">
      <h2>工單列表</h2>
      <el-button type="primary" @click="$router.push('/tickets/create')">
        <el-icon><Plus /></el-icon>
        創建工單
      </el-button>
    </div>

    <el-card>
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜尋工單標題或編號"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select v-model="searchForm.status" placeholder="狀態" clearable>
              <el-option label="全部" value="" />
              <el-option label="待審核" value="pending" />
              <el-option label="進行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
              <el-option label="已拒絕" value="rejected" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="handleSearch">搜尋</el-button>
          </el-col>
        </el-row>
      </div>

      <el-table :data="tickets" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="工單號" width="120" />
        <el-table-column prop="title" label="標題" min-width="200" />
        <el-table-column prop="type" label="類型" width="120" />
        <el-table-column prop="priority" label="優先級" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ scope.row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="狀態" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="處理人" width="120" />
        <el-table-column prop="created_at" label="創建時間" width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="viewTicket(scope.row.id)"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="editTicket(scope.row.id)"
              v-if="scope.row.status === 'pending'"
            >
              編輯
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = reactive({
  keyword: '',
  status: ''
})

const tickets = ref([
  {
    id: 'T001',
    title: '系統部署申請',
    type: '部署申請',
    priority: '高',
    status: 'pending',
    assignee: '張三',
    created_at: '2025-01-26 10:30'
  },
  {
    id: 'T002',
    title: '數據庫參數調整',
    type: '參數變更',
    priority: '中',
    status: 'in_progress',
    assignee: '李四',
    created_at: '2025-01-25 14:20'
  },
  {
    id: 'T003',
    title: '用戶權限修改',
    type: '權限變更',
    priority: '低',
    status: 'completed',
    assignee: '王五',
    created_at: '2025-01-24 09:15'
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

const handleSearch = () => {
  loading.value = true
  // 這裡調用 API 搜尋
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadTickets()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadTickets()
}

const viewTicket = (id: string) => {
  router.push(`/tickets/${id}`)
}

const editTicket = (id: string) => {
  router.push(`/tickets/${id}/edit`)
}

const loadTickets = () => {
  loading.value = true
  // 這裡調用 API 載入工單列表
  setTimeout(() => {
    total.value = 156
    loading.value = false
  }, 1000)
}

onMounted(() => {
  loadTickets()
})
</script>

<style scoped>
.ticket-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>