import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
console.log('API_BASE_URL:', API_BASE_URL)

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth-token')
      delete api.defaults.headers.common['Authorization']
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      toast.error('Access denied')
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (!error.response) {
      console.error('Network error details:', error)
      toast.error(`Network error: ${error.message || 'Please check your connection.'}`)
    }

    return Promise.reject(error)
  }
)

// API service functions
export const authAPI = {
  login: (email: string, password: string) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },
  register: (userData: any) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data: any) => api.put('/auth/me', data),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/auth/change-password', { current_password: currentPassword, new_password: newPassword }),
}

export default api