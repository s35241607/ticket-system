import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginForm } from '@/types/user'
import { login, getUserInfo, logout as apiLogout } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 狀態
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<User | null>(null)
  const permissions = ref<string[]>([])

  // 計算屬性
  const isLoggedIn = computed(() => !!token.value)
  const hasPermission = computed(() => (permission: string) => {
    return permissions.value.includes(permission)
  })

  // 動作
  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    localStorage.removeItem('token')
  }

  const setUserInfo = (info: User) => {
    userInfo.value = info
  }

  const setPermissions = (perms: string[]) => {
    permissions.value = perms
  }

  // 登入
  const loginAction = async (loginForm: LoginForm) => {
    try {
      const response = await login(loginForm)
      const { token: newToken, user } = response.data
      
      setToken(newToken)
      setUserInfo(user)
      
      // 獲取用戶權限
      await getUserInfoAction()
      
      return response
    } catch (error) {
      throw error
    }
  }

  // 獲取用戶信息
  const getUserInfoAction = async () => {
    try {
      const response = await getUserInfo()
      const { user, permissions: userPermissions } = response.data
      
      setUserInfo(user)
      setPermissions(userPermissions)
      
      return response
    } catch (error) {
      // 如果獲取用戶信息失敗，清除token
      clearToken()
      throw error
    }
  }

  // 登出
  const logout = async () => {
    try {
      await apiLogout()
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      clearToken()
      userInfo.value = null
      permissions.value = []
    }
  }

  // 重置狀態
  const reset = () => {
    clearToken()
    userInfo.value = null
    permissions.value = []
  }

  return {
    // 狀態
    token,
    userInfo,
    permissions,
    
    // 計算屬性
    isLoggedIn,
    hasPermission,
    
    // 動作
    setToken,
    clearToken,
    setUserInfo,
    setPermissions,
    loginAction,
    getUserInfoAction,
    logout,
    reset
  }
})