import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { api } from '@/lib/api'
import type { User, LoginCredentials, RegisterData } from '@/types'

// Helper functions for localStorage persistence
const getStoredUser = (): User | null => {
  const stored = localStorage.getItem('user')
  return stored ? JSON.parse(stored) : null
}

const setStoredUser = (user: User | null) => {
  if (user) {
    localStorage.setItem('user', JSON.stringify(user))
  } else {
    localStorage.removeItem('user')
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(getStoredUser())
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (credentials: LoginCredentials) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/auth/login', credentials)
      
      if (response.data.success) {
        if (
          response.data.access_token !== undefined && 
          response.data.access_token !== null && 
          response.data.access_token !== "")
        {
          token.value = response.data.access_token
          user.value = response.data.user
          if (token.value) {
            localStorage.setItem('token', token.value)
          }
          setStoredUser(user.value)
          return { success: true }
        }else {
          return {success:false}
        }
        
      } else {
        throw new Error('Login failed')
      }
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/auth/register', data)
      
      if (response.data.success) {
        return { success: true, user: response.data.user }
      } else {
        throw new Error('Registration failed')
      }
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Registration failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    setStoredUser(null)
  }

  const fetchUser = async () => {
    if (!token.value) return
    
    try {
      const response = await api.get('/users/me')
      if (response.data.success) {
        user.value = response.data.user
        setStoredUser(user.value)
      }
    } catch (err) {
      // If API call fails, don't automatically logout if we have cached user data
      // This allows offline functionality with cached data
      if (!user.value) {
        logout()
      }
    }
  }

  // Watch for changes and persist to localStorage
  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  })

  watch(user, (newUser) => {
    setStoredUser(newUser)
  })

  // Initialize auth state
  // No need to fetchUser if we already have user data from localStorage
  if (token.value && !user.value) {
    fetchUser()
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser
  }
})
