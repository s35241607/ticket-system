import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ticket, TicketListParams, CreateTicketForm, UpdateTicketForm } from '@/types/ticket'
import { 
  getTickets, 
  getTicket, 
  createTicket, 
  updateTicket, 
  deleteTicket,
  getTicketComments,
  addTicketComment,
  getTicketAttachments,
  uploadTicketAttachment,
  getTicketHistory
} from '@/api/ticket'

export const useTicketStore = defineStore('ticket', () => {
  // 狀態
  const tickets = ref<Ticket[]>([])
  const currentTicket = ref<Ticket | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 計算屬性
  const hasMore = computed(() => {
    return tickets.value.length < total.value
  })

  // 動作
  const fetchTickets = async (params?: TicketListParams) => {
    try {
      loading.value = true
      const response = await getTickets({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params
      })
      
      const { items, total: totalCount, page, pageSize: size } = response.data
      
      if (page === 1) {
        tickets.value = items
      } else {
        tickets.value.push(...items)
      }
      
      total.value = totalCount
      currentPage.value = page
      pageSize.value = size
      
      return response
    } catch (error) {
      console.error('Failed to fetch tickets:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchTicket = async (id: number) => {
    try {
      loading.value = true
      const response = await getTicket(id)
      currentTicket.value = response.data
      return response
    } catch (error) {
      console.error('Failed to fetch ticket:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createTicketAction = async (form: CreateTicketForm) => {
    try {
      loading.value = true
      const response = await createTicket(form)
      const newTicket = response.data
      
      // 添加到列表頂部
      tickets.value.unshift(newTicket)
      total.value += 1
      
      return response
    } catch (error) {
      console.error('Failed to create ticket:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateTicketAction = async (id: number, form: UpdateTicketForm) => {
    try {
      loading.value = true
      const response = await updateTicket(id, form)
      const updatedTicket = response.data
      
      // 更新列表中的票務
      const index = tickets.value.findIndex(t => t.id === id)
      if (index > -1) {
        tickets.value[index] = updatedTicket
      }
      
      // 更新當前票務
      if (currentTicket.value?.id === id) {
        currentTicket.value = updatedTicket
      }
      
      return response
    } catch (error) {
      console.error('Failed to update ticket:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteTicketAction = async (id: number) => {
    try {
      loading.value = true
      await deleteTicket(id)
      
      // 從列表中移除
      const index = tickets.value.findIndex(t => t.id === id)
      if (index > -1) {
        tickets.value.splice(index, 1)
        total.value -= 1
      }
      
      // 清除當前票務
      if (currentTicket.value?.id === id) {
        currentTicket.value = null
      }
    } catch (error) {
      console.error('Failed to delete ticket:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchTicketComments = async (ticketId: number) => {
    try {
      const response = await getTicketComments(ticketId)
      return response.data
    } catch (error) {
      console.error('Failed to fetch ticket comments:', error)
      throw error
    }
  }

  const addTicketCommentAction = async (ticketId: number, content: string) => {
    try {
      const response = await addTicketComment(ticketId, { content })
      return response.data
    } catch (error) {
      console.error('Failed to add ticket comment:', error)
      throw error
    }
  }

  const fetchTicketAttachments = async (ticketId: number) => {
    try {
      const response = await getTicketAttachments(ticketId)
      return response.data
    } catch (error) {
      console.error('Failed to fetch ticket attachments:', error)
      throw error
    }
  }

  const uploadTicketAttachmentAction = async (ticketId: number, file: File) => {
    try {
      const response = await uploadTicketAttachment(ticketId, file)
      return response.data
    } catch (error) {
      console.error('Failed to upload ticket attachment:', error)
      throw error
    }
  }

  const fetchTicketHistory = async (ticketId: number) => {
    try {
      const response = await getTicketHistory(ticketId)
      return response.data
    } catch (error) {
      console.error('Failed to fetch ticket history:', error)
      throw error
    }
  }

  const loadMore = async (params?: TicketListParams) => {
    if (!hasMore.value || loading.value) return
    
    currentPage.value += 1
    await fetchTickets(params)
  }

  const refresh = async (params?: TicketListParams) => {
    currentPage.value = 1
    await fetchTickets(params)
  }

  const reset = () => {
    tickets.value = []
    currentTicket.value = null
    total.value = 0
    currentPage.value = 1
    pageSize.value = 20
  }

  return {
    // 狀態
    tickets,
    currentTicket,
    loading,
    total,
    currentPage,
    pageSize,
    
    // 計算屬性
    hasMore,
    
    // 動作
    fetchTickets,
    fetchTicket,
    createTicketAction,
    updateTicketAction,
    deleteTicketAction,
    fetchTicketComments,
    addTicketCommentAction,
    fetchTicketAttachments,
    uploadTicketAttachmentAction,
    fetchTicketHistory,
    loadMore,
    refresh,
    reset
  }
})