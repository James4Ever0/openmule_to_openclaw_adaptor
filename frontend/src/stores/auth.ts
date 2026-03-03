import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/lib/api'
import type { User, LoginCredentials, RegisterData } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (credentials: LoginCredentials) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post('/auth/login', credentials)
      
      if (response.data.success) {
        token.value = response.data.access_token
        user.value = response.data.user
        
        localStorage.setItem('token', token.value)
        
        return { success: true }
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
  }

  const fetchUser = async () => {
    if (!token.value) return
    
    try {
      const response = await api.get('/users/me')
      if (response.data.success) {
        user.value = response.data.user
      }
    } catch (err) {
      logout()
    }
  }

  // Initialize auth state
  if (token.value) {
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
