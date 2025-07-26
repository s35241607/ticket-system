import type { User, Department } from './user'

export interface Ticket {
  id: number
  title: string
  description: string
  typeId: number
  type: TicketType
  statusId: number
  status: TicketStatus
  priorityId: number
  priority: TicketPriority
  departmentId: number
  department: Department
  assigneeId?: number
  assignee?: User
  reporterId: number
  reporter: User
  workflowId?: number
  workflow?: Workflow
  currentStepId?: number
  currentStep?: WorkflowStep
  dueDate?: string
  resolvedAt?: string
  closedAt?: string
  tags?: string[]
  customFields?: Record<string, any>
  attachments?: TicketAttachment[]
  comments?: TicketComment[]
  createdAt: string
  updatedAt: string
}

export interface TicketType {
  id: number
  name: string
  description?: string
  icon?: string
  color?: string
  workflowId?: number
  workflow?: Workflow
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface TicketStatus {
  id: number
  name: string
  description?: string
  color?: string
  isFinal: boolean
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface TicketPriority {
  id: number
  name: string
  description?: string
  level: number
  color?: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface Workflow {
  id: number
  name: string
  description?: string
  steps: WorkflowStep[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface WorkflowStep {
  id: number
  workflowId: number
  name: string
  description?: string
  stepOrder: number
  statusId: number
  status: TicketStatus
  assigneeType: 'user' | 'role' | 'department'
  assigneeId?: number
  isRequired: boolean
  timeLimit?: number
  conditions?: Record<string, any>
  actions?: Record<string, any>
  createdAt: string
  updatedAt: string
}

export interface TicketAttachment {
  id: number
  ticketId: number
  filename: string
  originalName: string
  mimeType: string
  size: number
  url: string
  uploadedById: number
  uploadedBy: User
  createdAt: string
}

export interface TicketComment {
  id: number
  ticketId: number
  content: string
  authorId: number
  author: User
  isInternal: boolean
  attachments?: TicketAttachment[]
  createdAt: string
  updatedAt: string
}

export interface TicketHistory {
  id: number
  ticketId: number
  action: string
  field?: string
  oldValue?: string
  newValue?: string
  description: string
  userId: number
  user: User
  createdAt: string
}

export interface WorkflowApproval {
  id: number
  ticketId: number
  stepId: number
  step: WorkflowStep
  approverId: number
  approver: User
  status: 'pending' | 'approved' | 'rejected'
  comment?: string
  approvedAt?: string
  createdAt: string
  updatedAt: string
}

export interface CreateTicketForm {
  title: string
  description: string
  typeId: number
  priorityId: number
  departmentId: number
  assigneeId?: number
  dueDate?: string
  tags?: string[]
  customFields?: Record<string, any>
  attachments?: File[]
}

export interface UpdateTicketForm {
  title?: string
  description?: string
  typeId?: number
  priorityId?: number
  departmentId?: number
  assigneeId?: number
  statusId?: number
  dueDate?: string
  tags?: string[]
  customFields?: Record<string, any>
}

export interface TicketListParams {
  page?: number
  pageSize?: number
  search?: string
  typeId?: number
  statusId?: number
  priorityId?: number
  departmentId?: number
  assigneeId?: number
  reporterId?: number
  dateFrom?: string
  dateTo?: string
  tags?: string[]
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface TicketListResponse {
  items: Ticket[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface TicketStats {
  total: number
  open: number
  inProgress: number
  resolved: number
  closed: number
  overdue: number
  byPriority: Record<string, number>
  byType: Record<string, number>
  byDepartment: Record<string, number>
}