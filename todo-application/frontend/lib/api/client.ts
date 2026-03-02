/**
 * Axios API client with authentication and error handling
 */
import axios, { AxiosError } from 'axios'
import { getApiBaseUrl } from '@/lib/config'

/**
 * Create axios instance with runtime URL detection
 * The baseURL is determined at runtime, not build time
 */
const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds (Neon DB cold start can take up to 30s)
})

// Set baseURL dynamically on each request for runtime detection
api.interceptors.request.use(
  (config) => {
    // Set baseURL at runtime (not build time)
    if (!config.baseURL) {
      config.baseURL = getApiBaseUrl()
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      // Clear token and redirect to signin
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        window.location.href = '/auth/signin'
      }
    }

    // Handle 403 Forbidden - user trying to access another user's resources
    if (error.response?.status === 403) {
      console.error('403 Forbidden: User is not authorized to access this resource. This may happen if you switch users without logging out properly.')
      // Clear token and redirect to signin to force fresh login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        alert('Session mismatch detected. Please log in again.')
        window.location.href = '/auth/signin'
      }
    }

    // Handle other errors
    return Promise.reject(error)
  }
)

export default api
