<template>
  <div class="settings">
    <div class="page-header">
      <h2>系統設置</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <el-menu
            :default-active="activeTab"
            class="settings-menu"
            @select="handleTabChange"
          >
            <el-menu-item index="general">
              <el-icon><Setting /></el-icon>
              <span>一般設置</span>
            </el-menu-item>
            <el-menu-item index="users">
              <el-icon><User /></el-icon>
              <span>用戶管理</span>
            </el-menu-item>
            <el-menu-item index="departments">
              <el-icon><OfficeBuilding /></el-icon>
              <span>部門管理</span>
            </el-menu-item>
            <el-menu-item index="notifications">
              <el-icon><Bell /></el-icon>
              <span>通知設置</span>
            </el-menu-item>
            <el-menu-item index="security">
              <el-icon><Lock /></el-icon>
              <span>安全設置</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card>
          <!-- 一般設置 -->
          <div v-if="activeTab === 'general'">
            <h3>一般設置</h3>
            <el-form :model="generalSettings" label-width="150px">
              <el-form-item label="系統名稱">
                <el-input v-model="generalSettings.systemName" />
              </el-form-item>
              <el-form-item label="系統描述">
                <el-input
                  v-model="generalSettings.systemDescription"
                  type="textarea"
                  :rows="3"
                />
              </el-form-item>
              <el-form-item label="工單編號前綴">
                <el-input v-model="generalSettings.ticketPrefix" />
              </el-form-item>
              <el-form-item label="預設優先級">
                <el-select v-model="generalSettings.defaultPriority">
                  <el-option label="低" value="low" />
                  <el-option label="中" value="medium" />
                  <el-option label="高" value="high" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveGeneralSettings">
                  保存設置
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 用戶管理 -->
          <div v-if="activeTab === 'users'">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
              <h3>用戶管理</h3>
              <el-button type="primary" @click="addUser">
                <el-icon><Plus /></el-icon>
                添加用戶
              </el-button>
            </div>
            <el-table :data="users" style="width: 100%">
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="email" label="郵箱" />
              <el-table-column prop="department" label="部門" />
              <el-table-column prop="role" label="角色" />
              <el-table-column prop="status" label="狀態">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
                    {{ scope.row.status === 'active' ? '啟用' : '停用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="editUser(scope.row)">
                    編輯
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteUser(scope.row.id)">
                    刪除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 部門管理 -->
          <div v-if="activeTab === 'departments'">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
              <h3>部門管理</h3>
              <el-button type="primary" @click="addDepartment">
                <el-icon><Plus /></el-icon>
                添加部門
              </el-button>
            </div>
            <el-table :data="departments" style="width: 100%">
              <el-table-column prop="name" label="部門名稱" />
              <el-table-column prop="description" label="描述" />
              <el-table-column prop="manager" label="部門主管" />
              <el-table-column prop="member_count" label="成員數量" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="editDepartment(scope.row)">
                    編輯
                  </el-button>
                  <el-button type="danger" size="small" @click="deleteDepartment(scope.row.id)">
                    刪除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 通知設置 -->
          <div v-if="activeTab === 'notifications'">
            <h3>通知設置</h3>
            <el-form :model="notificationSettings" label-width="200px">
              <el-form-item label="郵件通知">
                <el-switch v-model="notificationSettings.emailEnabled" />
              </el-form-item>
              <el-form-item label="工單創建通知">
                <el-switch v-model="notificationSettings.ticketCreated" />
              </el-form-item>
              <el-form-item label="工單狀態變更通知">
                <el-switch v-model="notificationSettings.statusChanged" />
              </el-form-item>
              <el-form-item label="工單分配通知">
                <el-switch v-model="notificationSettings.ticketAssigned" />
              </el-form-item>
              <el-form-item label="工單完成通知">
                <el-switch v-model="notificationSettings.ticketCompleted" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveNotificationSettings">
                  保存設置
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 安全設置 -->
          <div v-if="activeTab === 'security'">
            <h3>安全設置</h3>
            <el-form :model="securitySettings" label-width="200px">
              <el-form-item label="密碼最小長度">
                <el-input-number v-model="securitySettings.minPasswordLength" :min="6" :max="20" />
              </el-form-item>
              <el-form-item label="登入失敗鎖定次數">
                <el-input-number v-model="securitySettings.maxLoginAttempts" :min="3" :max="10" />
              </el-form-item>
              <el-form-item label="會話超時時間(分鐘)">
                <el-input-number v-model="securitySettings.sessionTimeout" :min="30" :max="480" />
              </el-form-item>
              <el-form-item label="啟用雙因子認證">
                <el-switch v-model="securitySettings.twoFactorEnabled" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveSecuritySettings">
                  保存設置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('general')

const generalSettings = reactive({
  systemName: '工單管理系統',
  systemDescription: '企業內部工單管理和審批系統',
  ticketPrefix: 'T',
  defaultPriority: 'medium'
})

const notificationSettings = reactive({
  emailEnabled: true,
  ticketCreated: true,
  statusChanged: true,
  ticketAssigned: true,
  ticketCompleted: false
})

const securitySettings = reactive({
  minPasswordLength: 8,
  maxLoginAttempts: 5,
  sessionTimeout: 120,
  twoFactorEnabled: false
})

const users = ref([
  {
    id: 1,
    name: '張三',
    email: 'zhang@example.com',
    department: '技術部',
    role: '開發工程師',
    status: 'active'
  },
  {
    id: 2,
    name: '李四',
    email: 'li@example.com',
    department: '運維部',
    role: '系統管理員',
    status: 'active'
  }
])

const departments = ref([
  {
    id: 1,
    name: '技術部',
    description: '負責系統開發和維護',
    manager: '王五',
    member_count: 12
  },
  {
    id: 2,
    name: '運維部',
    description: '負責系統運維和監控',
    manager: '趙六',
    member_count: 8
  }
])

const handleTabChange = (key: string) => {
  activeTab.value = key
}

const saveGeneralSettings = () => {
  ElMessage.success('一般設置已保存')
}

const saveNotificationSettings = () => {
  ElMessage.success('通知設置已保存')
}

const saveSecuritySettings = () => {
  ElMessage.success('安全設置已保存')
}

const addUser = () => {
  ElMessage.info('添加用戶功能開發中...')
}

const editUser = (user: any) => {
  ElMessage.info(`編輯用戶 ${user.name} 功能開發中...`)
}

const deleteUser = (id: number) => {
  ElMessage.info(`刪除用戶 ${id} 功能開發中...`)
}

const addDepartment = () => {
  ElMessage.info('添加部門功能開發中...')
}

const editDepartment = (dept: any) => {
  ElMessage.info(`編輯部門 ${dept.name} 功能開發中...`)
}

const deleteDepartment = (id: number) => {
  ElMessage.info(`刪除部門 ${id} 功能開發中...`)
}
</script>

<style scoped>
.settings {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.settings-menu {
  border: none;
}

.settings-menu .el-menu-item {
  border-radius: 6px;
  margin-bottom: 4px;
}
</style>