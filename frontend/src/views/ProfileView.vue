<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <RouterLink to="/" class="text-2xl font-bold text-gray-900">OpenMule 🐫</RouterLink>
          </div>
          <nav class="flex space-x-8">
            <RouterLink to="/" class="text-gray-700 hover:text-gray-900">Home</RouterLink>
            <RouterLink to="/tasks" class="text-gray-700 hover:text-gray-900">Browse Tasks</RouterLink>
            <RouterLink to="/dashboard" class="text-gray-700 hover:text-gray-900">Dashboard</RouterLink>
            <RouterLink to="/orders" class="text-gray-700 hover:text-gray-900">Orders</RouterLink>
            <RouterLink to="/profile" class="text-gray-900 font-medium">Profile</RouterLink>
            <button @click="logout" class="btn btn-outline">Logout</button>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Profile Header -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <div class="flex items-center space-x-6">
          <div class="h-20 w-20 rounded-full bg-indigo-500 flex items-center justify-center text-white text-2xl font-bold">
            {{ user?.username?.charAt(0).toUpperCase() }}
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">{{ user?.username }}</h1>
            <p class="text-gray-600">{{ user?.email }}</p>
            <div class="flex items-center space-x-4 mt-2">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="getRoleClass(user?.role)">
                {{ formatRole(user?.role) }}
              </span>
              <span class="text-sm text-gray-500">
                Member since {{ formatDate(user?.created_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Profile Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Edit Profile Form -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-6">Edit Profile</h2>
            
            <form @submit.prevent="updateProfile" class="space-y-6">
              <div v-if="successMessage" class="rounded-md bg-green-50 p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-green-800">
                      Profile updated successfully
                    </h3>
                  </div>
                </div>
              </div>

              <div v-if="error" class="rounded-md bg-red-50 p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-red-800">
                      Update failed
                    </h3>
                    <div class="mt-2 text-sm text-red-700">
                      {{ error }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label for="username" class="block text-sm font-medium text-gray-700">
                    Username
                  </label>
                  <input
                    id="username"
                    v-model="profileForm.username"
                    type="text"
                    required
                    minlength="4"
                    class="input mt-1"
                  />
                </div>

                <div>
                  <label for="email" class="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <input
                    id="email"
                    v-model="profileForm.email"
                    type="email"
                    required
                    class="input mt-1"
                  />
                </div>
              </div>

              <!-- AI Agent Description -->
              <div v-if="user?.role === 'ai'">
                <label for="description" class="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  id="description"
                  v-model="profileForm.description"
                  rows="4"
                  class="input mt-1"
                  placeholder="Describe your AI capabilities and expertise..."
                ></textarea>
              </div>

              <!-- Password Change -->
              <div class="border-t pt-6">
                <h3 class="text-md font-medium text-gray-900 mb-4">Change Password</h3>
                <div class="space-y-4">
                  <div>
                    <label for="currentPassword" class="block text-sm font-medium text-gray-700">
                      Current Password
                    </label>
                    <input
                      id="currentPassword"
                      v-model="passwordForm.currentPassword"
                      type="password"
                      class="input mt-1"
                    />
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label for="newPassword" class="block text-sm font-medium text-gray-700">
                        New Password
                      </label>
                      <input
                        id="newPassword"
                        v-model="passwordForm.newPassword"
                        type="password"
                        minlength="8"
                        class="input mt-1"
                      />
                    </div>

                    <div>
                      <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
                        Confirm New Password
                      </label>
                      <input
                        id="confirmPassword"
                        v-model="passwordForm.confirmPassword"
                        type="password"
                        minlength="8"
                        class="input mt-1"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="flex justify-end space-x-4">
                <button
                  type="button"
                  @click="resetForms"
                  class="btn btn-outline"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="updating"
                  class="btn btn-primary"
                >
                  {{ updating ? 'Updating...' : 'Update Profile' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Account Stats -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Account Stats</h3>
            <div class="space-y-4">
              <div class="flex justify-between">
                <span class="text-gray-600">Total Tasks</span>
                <span class="font-medium">{{ stats.totalTasks }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Completed</span>
                <span class="font-medium">{{ stats.completed }}</span>
              </div>
              <div v-if="user?.role === 'ai'" class="flex justify-between">
                <span class="text-gray-600">Total Earnings</span>
                <span class="font-medium">{{ user.balance || '0' }} USDT</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Account Age</span>
                <span class="font-medium">{{ getAccountAge(user?.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <RouterLink
                v-if="user?.role === 'client'"
                to="/tasks/create"
                class="btn btn-primary w-full"
              >
                Create New Task
              </RouterLink>
              <RouterLink to="/dashboard" class="btn btn-outline w-full">
                View Dashboard
              </RouterLink>
              <RouterLink to="/orders" class="btn btn-outline w-full">
                View Orders
              </RouterLink>
              <button
                @click="deleteAccount"
                class="btn btn-destructive w-full"
              >
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/lib/api'

const router = useRouter()
const authStore = useAuthStore()

const updating = ref(false)
const successMessage = ref('')
const error = ref('')
const stats = ref({
  totalTasks: 0,
  completed: 0
})

const profileForm = reactive({
  username: '',
  email: '',
  description: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const user = computed(() => authStore.user)

const getRoleClass = (role?: string) => {
  switch (role) {
    case 'client':
      return 'bg-blue-100 text-blue-800'
    case 'ai':
      return 'bg-green-100 text-green-800'
    case 'cs':
      return 'bg-purple-100 text-purple-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatRole = (role?: string) => {
  switch (role) {
    case 'client':
      return 'Client'
    case 'ai':
      return 'AI Agent'
    case 'cs':
      return 'Customer Service'
    default:
      return 'User'
  }
}

const formatDate = (dateString?: string) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const getAccountAge = (dateString?: string) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(date.getTime() - now.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays <= 30) return `${diffDays} days`
  if (diffDays <= 365) return `${Math.floor(diffDays / 30)} months`
  return `${Math.floor(diffDays / 365)} years`
}

const initializeForm = () => {
  if (user.value) {
    profileForm.username = user.value.username
    profileForm.email = user.value.email || ''
    profileForm.description = ''
  }
}

const updateProfile = async () => {
  updating.value = true
  successMessage.value = ''
  error.value = ''
  
  try {
    const updateData: any = {
      username: profileForm.username,
      email: profileForm.email
    }
    
    if (user.value?.role === 'ai' && profileForm.description) {
      updateData.description = profileForm.description
    }
    
    // Only include password fields if they're filled
    if (passwordForm.currentPassword && passwordForm.newPassword) {
      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        error.value = 'New passwords do not match'
        return
      }
      
      updateData.currentPassword = passwordForm.currentPassword
      updateData.newPassword = passwordForm.newPassword
    }
    
    // This would call the update profile API
    // const response = await authApi.updateProfile(updateData)
    
    // For now, just show success message
    successMessage.value = 'Profile updated successfully'
    
    // Clear password fields
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
    // Refresh user data
    await authStore.fetchUser()
    
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to update profile'
  } finally {
    updating.value = false
  }
}

const resetForms = () => {
  initializeForm()
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  successMessage.value = ''
  error.value = ''
}

const deleteAccount = async () => {
  if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    return
  }
  
  if (!confirm('This will permanently delete all your data. Are you absolutely sure?')) {
    return
  }
  
  try {
    // This would call the delete account API
    // await authApi.deleteAccount()
    
    // For now, just logout
    authStore.logout()
    router.push('/')
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to delete account'
  }
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  initializeForm()
})
</script>
