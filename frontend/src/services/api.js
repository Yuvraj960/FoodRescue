import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: inject JWT bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('foodrescue_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle token expiry
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If token expired or invalid, clear storage
      localStorage.removeItem('foodrescue_token')
      localStorage.removeItem('foodrescue_user')
    }
    return Promise.reject(error)
  }
)

export default api
