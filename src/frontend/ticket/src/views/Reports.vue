<template>
  <div class="reports">
    <div class="page-header">
      <h2>報表分析</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>工單狀態統計</span>
          </template>
          <div class="chart-container">
            <div class="chart-placeholder">
              📊 圖表區域 (待整合 ECharts)
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>工單類型分布</span>
          </template>
          <div class="chart-container">
            <div class="chart-placeholder">
              📈 圖表區域 (待整合 ECharts)
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>工單處理趨勢</span>
          </template>
          <div class="chart-container" style="height: 300px;">
            <div class="chart-placeholder">
              📉 趨勢圖表區域 (待整合 ECharts)
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>詳細報表</span>
              <el-button type="primary" @click="exportReport">
                <el-icon><Download /></el-icon>
                導出報表
              </el-button>
            </div>
          </template>
          <el-table :data="reportData" style="width: 100%">
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="total" label="總工單數" width="100" />
            <el-table-column prop="created" label="新建" width="80" />
            <el-table-column prop="pending" label="待審核" width="80" />
            <el-table-column prop="in_progress" label="進行中" width="80" />
            <el-table-column prop="completed" label="已完成" width="80" />
            <el-table-column prop="rejected" label="已拒絕" width="80" />
            <el-table-column prop="completion_rate" label="完成率" width="100">
              <template #default="scope">
                {{ scope.row.completion_rate }}%
              </template>
            </el-table-column>
            <el-table-column prop="avg_processing_time" label="平均處理時間" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const reportData = ref([
  {
    date: '2025-01-26',
    total: 25,
    created: 8,
    pending: 5,
    in_progress: 7,
    completed: 12,
    rejected: 1,
    completion_rate: 85.2,
    avg_processing_time: '2.3天'
  },
  {
    date: '2025-01-25',
    total: 32,
    created: 12,
    pending: 3,
    in_progress: 8,
    completed: 18,
    rejected: 3,
    completion_rate: 78.9,
    avg_processing_time: '2.8天'
  },
  {
    date: '2025-01-24',
    total: 28,
    created: 6,
    pending: 4,
    in_progress: 6,
    completed: 16,
    rejected: 2,
    completion_rate: 82.1,
    avg_processing_time: '2.1天'
  }
])

const exportReport = () => {
  ElMessage.success('報表導出功能開發中...')
}

onMounted(() => {
  // 載入報表數據
})
</script>

<style scoped>
.reports {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.chart-container {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  font-size: 24px;
  color: #999;
  text-align: center;
}
</style>