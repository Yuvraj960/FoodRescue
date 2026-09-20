import { defineStore } from 'pinia'
import api from '../services/api'

export const useFoodStore = defineStore('food', {
  state: () => ({
    listings: [],
    currentListing: null,
    categories: [],
    loading: false,
    error: null,
    filters: {
      search: '',
      category_id: '',
      dietary_type: 'ALL',
      city: '',
    }
  }),

  actions: {
    async fetchCategories() {
      try {
        const response = await api.get('/auth/categories')
        this.categories = response.data
      } catch (err) {
        console.error('Failed to fetch categories', err)
      }
    },

    async fetchListings(customParams = {}) {
      this.loading = true
      this.error = null
      try {
        const params = {
          ...this.filters,
          ...customParams
        }
        // clean empty params
        Object.keys(params).forEach(k => {
          if (!params[k] || params[k] === 'ALL') delete params[k]
        })

        const response = await api.get('/food', { params })
        this.listings = response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to fetch listings'
      } finally {
        this.loading = false
      }
    },

    async fetchListing(id) {
      this.loading = true
      try {
        const response = await api.get(`/food/${id}`)
        this.currentListing = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to fetch food details'
        throw err
      } finally {
        this.loading = false
      }
    },

    async createListing(payload) {
      this.loading = true
      try {
        const response = await api.post('/food', payload)
        return { success: true, listing: response.data.listing }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Failed to create listing' }
      } finally {
        this.loading = false
      }
    },

    async reserveFood(listingId, quantity, notes = '') {
      try {
        const response = await api.post(`/food/${listingId}/reserve`, { quantity, notes })
        return { success: true, data: response.data }
      } catch (err) {
        return { success: false, error: err.response?.data?.error || 'Reservation failed' }
      }
    }
  }
})
