import { defineStore } from 'pinia'
import api from '../services/api'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
  }),

  actions: {
    async fetchNotifications() {
      this.loading = true
      try {
        const response = await api.get('/notifications')
        this.notifications = response.data
        this.unreadCount = this.notifications.filter(n => !n.is_read).length
      } catch (err) {
        console.error('Failed to fetch notifications', err)
      } finally {
        this.loading = false
      }
    },

    async fetchUnreadCount() {
      try {
        const response = await api.get('/notifications/unread-count')
        this.unreadCount = response.data.unread_count
      } catch (err) {
        console.error('Failed to fetch unread count', err)
      }
    },

    async markAsRead(id) {
      try {
        await api.put(`/notifications/${id}/read`)
        const n = this.notifications.find(item => item.id === id)
        if (n && !n.is_read) {
          n.is_read = true
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        }
      } catch (err) {
        console.error('Failed to mark notification read', err)
      }
    },

    async markAllRead() {
      try {
        await api.put('/notifications/read-all')
        this.notifications.forEach(n => n.is_read = true)
        this.unreadCount = 0
      } catch (err) {
        console.error('Failed to mark all read', err)
      }
    }
  }
})
