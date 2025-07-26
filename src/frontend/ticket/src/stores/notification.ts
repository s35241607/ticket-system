import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types/notification'
import { getNotifications, markAsRead, markAllAsRead } from '@/api/notification'

export const useNotificationStore = defineStore('notification', () => {
  // 狀態
  const notifications = ref<Notification[]>([])
  const loading = ref(false)

  // 計算屬性
  const unreadCount = computed(() => {
    return notifications.value.filter(n => !n.isRead).length
  })

  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => !n.isRead)
  })

  // 動作
  const fetchNotifications = async (params?: {
    page?: number
    pageSize?: number
    isRead?: boolean
  }) => {
    try {
      loading.value = true
      const response = await getNotifications(params)
      notifications.value = response.data.items
      return response
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const markNotificationAsRead = async (id: number) => {
    try {
      await markAsRead(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.isRead = true
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      throw error
    }
  }

  const markAllNotificationsAsRead = async () => {
    try {
      await markAllAsRead()
      notifications.value.forEach(n => {
        n.isRead = true
      })
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
      throw error
    }
  }

  const addNotification = (notification: Notification) => {
    notifications.value.unshift(notification)
  }

  const removeNotification = (id: number) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearNotifications = () => {
    notifications.value = []
  }

  return {
    // 狀態
    notifications,
    loading,
    
    // 計算屬性
    unreadCount,
    unreadNotifications,
    
    // 動作
    fetchNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    addNotification,
    removeNotification,
    clearNotifications
  }
})