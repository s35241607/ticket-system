<template>
  <div class="workflow-list">
    <div class="page-header">
      <h2>工作流程管理</h2>
      <el-button type="primary" @click="createWorkflow">
        <el-icon><Plus /></el-icon>
        創建工作流程
      </el-button>
    </div>

    <el-card>
      <el-table :data="workflows" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="工作流程名稱" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="steps" label="步驟數" width="100" />
        <el-table-column prop="status" label="狀態" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '啟用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="創建時間" width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editWorkflow(scope.row.id)">
              編輯
            </el-button>
            <el-button
              :type="scope.row.status === 'active' ? 'warning' : 'success'"
              size="small"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 'active' ? '停用' : '啟用' }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteWorkflow(scope.row.id)">
              刪除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)

const workflows = ref([
  {
    id: 1,
    name: '標準工單審批流程',
    description: '適用於一般工單的標準審批流程，包含部門主管審批和技術負責人審批',
    steps: 3,
    status: 'active',
    created_at: '2025-01-20'
  },
  {
    id: 2,
    name: '緊急工單快速流程',
    description: '適用於緊急工單的快速審批流程，僅需技術負責人審批',
    steps: 2,
    status: 'active',
    created_at: '2025-01-18'
  },
  {
    id: 3,
    name: '高風險變更審批流程',
    description: '適用於高風險變更的嚴格審批流程，需要多級審批',
    steps: 5,
    status: 'inactive',
    created_at: '2025-01-15'
  }
])

const createWorkflow = () => {
  ElMessage.info('創建工作流程功能開發中...')
}

const editWorkflow = (id: number) => {
  ElMessage.info(`編輯工作流程 ${id} 功能開發中...`)
}

const toggleStatus = async (workflow: any) => {
  try {
    await ElMessageBox.confirm(
      `確定要${workflow.status === 'active' ? '停用' : '啟用'}此工作流程嗎？`,
      '確認操作',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    workflow.status = workflow.status === 'active' ? 'inactive' : 'active'
    ElMessage.success(`工作流程已${workflow.status === 'active' ? '啟用' : '停用'}`)
  } catch {
    // 用戶取消操作
  }
}

const deleteWorkflow = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      '確定要刪除此工作流程嗎？此操作不可恢復！',
      '確認刪除',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = workflows.value.findIndex(w => w.id === id)
    if (index > -1) {
      workflows.value.splice(index, 1)
      ElMessage.success('工作流程已刪除')
    }
  } catch {
    // 用戶取消操作
  }
}

onMounted(() => {
  // 載入工作流程列表
})
</script>

<style scoped>
.workflow-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>