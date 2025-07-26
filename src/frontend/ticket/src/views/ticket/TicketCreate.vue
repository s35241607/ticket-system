<template>
  <div class="ticket-create">
    <div class="page-header">
      <h2>創建工單</h2>
    </div>

    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        @submit.prevent
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工單標題" prop="title">
              <el-input v-model="form.title" placeholder="請輸入工單標題" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工單類型" prop="type">
              <el-select v-model="form.type" placeholder="請選擇工單類型" style="width: 100%">
                <el-option label="部署申請" value="deployment" />
                <el-option label="參數變更" value="parameter_change" />
                <el-option label="權限變更" value="permission_change" />
                <el-option label="數據修改" value="data_modification" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="優先級" prop="priority">
              <el-select v-model="form.priority" placeholder="請選擇優先級" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="緊急" value="urgent" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="預期完成時間" prop="expected_completion">
              <el-date-picker
                v-model="form.expected_completion"
                type="datetime"
                placeholder="選擇預期完成時間"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="工單描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="6"
            placeholder="請詳細描述工單內容、需求和預期結果"
          />
        </el-form-item>

        <el-form-item label="附件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            multiple
            :auto-upload="false"
            :file-list="fileList"
            @change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              將文件拖到此處，或<em>點擊上傳</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 jpg/png/pdf/doc/docx 文件，且不超過 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">
            提交工單
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const fileList = ref<UploadFile[]>([])

const form = reactive({
  title: '',
  type: '',
  priority: 'medium',
  expected_completion: '',
  description: ''
})

const rules: FormRules = {
  title: [
    { required: true, message: '請輸入工單標題', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '請選擇工單類型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '請選擇優先級', trigger: 'change' }
  ],
  description: [
    { required: true, message: '請輸入工單描述', trigger: 'blur' },
    { min: 10, message: '描述至少需要10個字符', trigger: 'blur' }
  ]
}

const handleFileChange = (file: UploadFile, files: UploadFile[]) => {
  fileList.value = files
}

const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      
      // 模擬提交請求
      setTimeout(() => {
        loading.value = false
        ElMessage.success('工單創建成功')
        router.push('/tickets')
      }, 2000)
    }
  })
}

const resetForm = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
  fileList.value = []
}
</script>

<style scoped>
.ticket-create {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.upload-demo {
  width: 100%;
}
</style>