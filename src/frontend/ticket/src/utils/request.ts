import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { ApiResponse, ApiError } from '@/types/api'

// 創建axios實例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    
    // 添加認證token
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    // 添加請求時間戳
    config.metadata = { startTime: new Date() }
    
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 響應攔截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response
    
    // 計算請求耗時
    const endTime = new Date()
    const startTime = response.config.metadata?.startTime
    if (startTime) {
      const duration = endTime.getTime() - startTime.getTime()
      console.log(`API ${response.config.url} took ${duration}ms`)
    }
    
    // 檢查業務狀態碼
    if (data.success === false) {
      const error: ApiError = {
        success: false,
        message: data.message || '請求失敗',
        code: data.code,
        details: data.data
      }
      
      // 顯示錯誤消息
      ElMessage.error(error.message)
      
      return Promise.reject(error)
    }
    
    return response
  },
  async (error) => {
    const { response, config } = error
    
    // 網絡錯誤
    if (!response) {
      ElMessage.error('網絡連接失敗，請檢查網絡設置')
      return Promise.reject(error)
    }
    
    const { status, data } = response
    const userStore = useUserStore()
    
    switch (status) {
      case 401:
        // 未授權，清除token並跳轉到登錄頁
        ElMessage.error('登錄已過期，請重新登錄')
        userStore.logout()
        window.location.href = '/login'
        break
        
      case 403:
        ElMessage.error('沒有權限執行此操作')
        break
        
      case 404:
        ElMessage.error('請求的資源不存在')
        break
        
      case 422:
        // 表單驗證錯誤
        const validationErrors = data?.details || {}
        const errorMessages = Object.values(validationErrors).flat()
        if (errorMessages.length > 0) {
          ElMessage.error(errorMessages[0] as string)
        } else {
          ElMessage.error(data?.message || '請求參數錯誤')
        }
        break
        
      case 429:
        ElMessage.error('請求過於頻繁，請稍後再試')
        break
        
      case 500:
        ElMessage.error('服務器內部錯誤，請聯繫管理員')
        break
        
      case 502:
      case 503:
      case 504:
        ElMessage.error('服務暫時不可用，請稍後再試')
        break
        
      default:
        ElMessage.error(data?.message || `請求失敗 (${status})`)
    }
    
    return Promise.reject(error)
  }
)

// 請求方法封裝
export const http = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return request.get(url, config)
  },
  
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return request.post(url, data, config)
  },
  
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return request.put(url, data, config)
  },
  
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return request.patch(url, data, config)
  },
  
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    return request.delete(url, config)
  },
  
  upload<T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    const formData = new FormData()
    formData.append('file', file)
    
    return request.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers
      }
    })
  }
}

export default request

// 擴展AxiosRequestConfig類型
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: Date
    }
  }
}