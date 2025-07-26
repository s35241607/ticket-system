import type { User } from './user'

export interface Notification {
  id: number
  title: string
  message: string
  type: NotificationType
  userId: number
  user?: User
  isRead: boolean
  data?: Record<string, any>
  readAt?: string
  createdAt: string
  updatedAt: string
}

export type NotificationType = 
  | 'ticket_created'
  | 'ticket_updated'
  | 'ticket_assigned'
  | 'ticket_commented'
  | 'ticket_approved'
  | 'ticket_rejected'
  | 'ticket_overdue'
  | 'workflow_step_completed'
  | 'system_maintenance'
  | 'general'

export interface NotificationListParams {
  page?: number
  pageSize?: number
  type?: NotificationType
  isRead?: boolean
  dateFrom?: string
  dateTo?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface NotificationListResponse {
  items: Notification[]
  total: number
  page: number
  pageSize: number
  totalPages: number
  unreadCount: number
}

export interface CreateNotificationForm {
  title: string
  message: string
  type: NotificationType
  userId?: number
  userIds?: number[]
  data?: Record<string, any>
}

export interface NotificationSettings {
  id: number
  userId: number
  emailEnabled: boolean
  pushEnabled: boolean
  smsEnabled: boolean
  ticketCreated: boolean
  ticketUpdated: boolean
  ticketAssigned: boolean
  ticketCommented: boolean
  ticketApproved: boolean
  ticketRejected: boolean
  ticketOverdue: boolean
  workflowStepCompleted: boolean
  systemMaintenance: boolean
  createdAt: string
  updatedAt: string
}