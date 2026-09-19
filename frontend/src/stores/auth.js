import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('foodrescue_token') || null,
    user: JSON.parse(localStorage.getItem('foodrescue_user') || 'null'),
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    role: (state) => state.user?.role || null,
    isProvider: (state) => state.user?.role === 'provider',
    isRecipient: (state) => state.user?.role === 'recipient',
    isAdmin: (state) => state.user?.role === 'admin',
    userName: (state) => state.user?.name || 'User',
    orgName: (state) => state.user?.organization?.name || '',
  },

  actions: {
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/login', { email, password })
        this.token = response.data.token
        this.user = response.data.user
        localStorage.setItem('foodrescue_token', this.token)
        localStorage.setItem('foodrescue_user', JSON.stringify(this.user))
        return { success: true }
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed. Please check your credentials.'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async register(payload) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/register', payload)
        this.token = response.data.token
        this.user = response.data.user
        localStorage.setItem('foodrescue_token', this.token)
        localStorage.setItem('foodrescue_user', JSON.stringify(this.user))
        return { success: true }
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed.'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      if (!this.token) return
      try {
        const response = await api.get('/auth/me')
        this.user = response.data.user
        localStorage.setItem('foodrescue_user', JSON.stringify(this.user))
      } catch (err) {
        this.logout()
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('foodrescue_token')
      localStorage.removeItem('foodrescue_user')
    }
  }
})
