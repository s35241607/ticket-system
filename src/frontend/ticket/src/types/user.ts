export interface User {
  id: number
  username: string
  email: string
  name: string
  avatar?: string
  phone?: string
  departmentId?: number
  department?: Department
  role: UserRole
  isActive: boolean
  lastLoginAt?: string
  createdAt: string
  updatedAt: string
}

export interface Department {
  id: number
  name: string
  description?: string
  managerId?: number
  manager?: User
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface UserRole {
  id: number
  name: string
  description?: string
  permissions: Permission[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface Permission {
  id: number
  name: string
  code: string
  description?: string
  resource: string
  action: string
  createdAt: string
  updatedAt: string
}

export interface LoginForm {
  username: string
  password: string
  remember?: boolean
}

export interface RegisterForm {
  username: string
  email: string
  name: string
  password: string
  confirmPassword: string
  phone?: string
  departmentId?: number
}

export interface UpdateUserForm {
  email?: string
  name?: string
  phone?: string
  departmentId?: number
  avatar?: string
}

export interface ChangePasswordForm {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

export interface UserListParams {
  page?: number
  pageSize?: number
  search?: string
  departmentId?: number
  roleId?: number
  isActive?: boolean
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface UserListResponse {
  items: User[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}