import toast from 'react-hot-toast'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authAPI } from '../services/api'

export interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: 'student' | 'teacher' | 'admin'
  jlpt_level?: string
  avatar_url?: string
  bio?: string
  study_streak: number
  total_study_time: number
  is_active: boolean
  created_at: string
  last_login?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  updateProfile: (data: Partial<User>) => Promise<void>
  initializeAuth: () => void
}

interface RegisterData {
  email: string
  username: string
  full_name: string
  password: string
  role?: 'student' | 'teacher'
  jlpt_level?: string
  bio?: string
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,

      initializeAuth: () => {
        const token = localStorage.getItem('auth-token')
        if (token) {
          authAPI.getProfile()
            .then(response => {
              set({ user: response.data, token })
            })
            .catch(() => {
              // Token is invalid, clear it
              localStorage.removeItem('auth-token')
              set({ user: null, token: null })
            })
        }
      },

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await authAPI.login(email, password)
          const { access_token, user } = response.data

          // Store token
          localStorage.setItem('auth-token', access_token)

          set({
            user,
            token: access_token,
            isLoading: false
          })

          toast.success(`Welcome back, ${user.full_name}!`)
        } catch (error: any) {
          set({ isLoading: false })
          const message = error.response?.data?.detail || 'Login failed'
          toast.error(message)
          throw error
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true })
        try {
          const response = await authAPI.register(userData)

          toast.success('Registration successful! Please log in.')
          set({ isLoading: false })

          // Auto-login after registration
          await get().login(userData.email, userData.password)
        } catch (error: any) {
          set({ isLoading: false })
          const message = error.response?.data?.detail || 'Registration failed'
          toast.error(message)
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('auth-token')
        set({ user: null, token: null })
        toast.success('Logged out successfully')
      },

      updateProfile: async (data: Partial<User>) => {
        try {
          const response = await authAPI.updateProfile(data)
          const updatedUser = response.data

          set({ user: updatedUser })
          toast.success('Profile updated successfully')
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Failed to update profile'
          toast.error(message)
          throw error
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token
      }),
    }
  )
)