export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: string
  timestamp?: string
}

export interface ApiError {
  success: false
  message: string
  code?: string
  details?: any
  timestamp?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ListParams {
  page?: number
  pageSize?: number
  search?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface UploadResponse {
  filename: string
  originalName: string
  mimeType: string
  size: number
  url: string
}

export interface FileUploadOptions {
  maxSize?: number
  allowedTypes?: string[]
  multiple?: boolean
}