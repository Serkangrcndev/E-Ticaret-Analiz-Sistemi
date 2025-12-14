import axios from 'axios'
import { API_BASE_URL } from '../utils/constants'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 dakika (scraping uzun sürebilir)
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      // Server responded with error
      return Promise.reject({
        message: error.response.data?.error || error.response.data?.message || 'Bir hata oluştu',
        status: error.response.status
      })
    } else if (error.request) {
      // Request made but no response
      return Promise.reject({
        message: 'Sunucuya bağlanılamadı. Lütfen backend\'in çalıştığından emin olun.',
        status: 0
      })
    } else {
      // Error in request setup
      return Promise.reject({
        message: error.message || 'Bir hata oluştu',
        status: 0
      })
    }
  }
)

export const apiService = {
  // Health check
  checkHealth: async () => {
    const response = await api.get('/api/health')
    return response.data
  },

  // Database status
  checkDbStatus: async () => {
    const response = await api.get('/api/db-status')
    return response.data
  },

  // Analyze site
  analyzeSite: async (url) => {
    const response = await api.post('/api/analyze', { url })
    return response.data
  },

  // Get site info
  getSiteInfo: async (domain) => {
    const response = await api.get(`/api/site/${domain}`)
    return response.data
  },

  // Get all sites
  getAllSites: async () => {
    const response = await api.get('/api/sites')
    return response.data
  },

  // Initialize database
  initDatabase: async () => {
    const response = await api.post('/api/init-db')
    return response.data
  }
}

export default api

