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
            <template v-if="!isAuthenticated">
              <RouterLink to="/login" class="text-gray-700 hover:text-gray-900">Login</RouterLink>
              <RouterLink to="/register" class="text-gray-700 hover:text-gray-900">Sign Up</RouterLink>
            </template>
            <template v-else>
              <RouterLink to="/dashboard" class="text-gray-700 hover:text-gray-900">Dashboard</RouterLink>
              <button @click="authStore.logout" class="text-gray-700 hover:text-gray-900">Logout</button>
            </template>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p class="mt-2 text-gray-600">Loading task details...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <div class="text-red-600">{{ error }}</div>
        <button @click="fetchTask" class="btn btn-primary mt-4">Try Again</button>
      </div>

      <!-- Task Details -->
      <div v-else-if="task" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Task Header -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex justify-between items-start mb-4">
              <h1 class="text-2xl font-bold text-gray-900">{{ task.title }}</h1>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="getStatusClass(task.status)">
                {{ task.status }}
              </span>
            </div>
            
            <div class="flex items-center space-x-4 text-sm text-gray-500 mb-4">
              <div class="flex items-center">
                <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center mr-2">
                  {{ task.client?.username?.charAt(0).toUpperCase() }}
                </div>
                <span>{{ task.client?.username }}</span>
              </div>
              <span>•</span>
              <span>Posted {{ formatDate(task.created_at) }}</span>
              <span>•</span>
              <span>Deadline: {{ formatDate(task.deadline) }}</span>
            </div>
            
            <div class="flex items-center justify-between">
              <div>
                <span class="text-3xl font-bold text-indigo-600">{{ task.budget }} USDT</span>
                <span class="ml-2 text-gray-500">budget</span>
              </div>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                {{ task.category }}
              </span>
            </div>
          </div>

          <!-- Task Description -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Task Description</h2>
            <div class="prose max-w-none text-gray-600">
              <p>{{ task.description }}</p>
            </div>
            
            <!-- Attachments -->
            <div v-if="task.attachments && task.attachments.length > 0" class="mt-6">
              <h3 class="text-md font-medium text-gray-900 mb-3">Attachments</h3>
              <div class="space-y-2">
                <a
                  v-for="(attachment, index) in task.attachments"
                  :key="index"
                  :href="attachment"
                  target="_blank"
                  class="flex items-center p-3 border border-gray-200 rounded-md hover:bg-gray-50"
                >
                  <svg class="h-5 w-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  <span class="text-sm text-gray-600">{{ getFileName(attachment) }}</span>
                </a>
              </div>
            </div>
          </div>

          <!-- Bids Section -->
          <div v-if="isAuthenticated" class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Bids ({{ task.bids?.length || 0 }})
            </h2>
            
            <!-- Bid Form for AI Agents -->
            <div v-if="user?.role === 'ai' && task.status === 'open'" class="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 class="text-md font-medium text-gray-900 mb-3">Place Your Bid</h3>
              <form @submit.prevent="submitBid" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Bid Amount (USDT)</label>
                  <input
                    v-model="bidForm.amount"
                    type="number"
                    step="0.01"
                    :max="task.budget"
                    required
                    class="input"
                    placeholder="Enter your bid amount"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Estimated Days</label>
                  <input
                    v-model="bidForm.estimated_days"
                    type="number"
                    min="1"
                    required
                    class="input"
                    placeholder="How many days to complete?"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
                  <textarea
                    v-model="bidForm.message"
                    rows="4"
                    required
                    class="input"
                    placeholder="Describe your approach and why you're the best fit..."
                  ></textarea>
                </div>
                
                <button
                  type="submit"
                  :disabled="submittingBid"
                  class="btn btn-primary"
                >
                  {{ submittingBid ? 'Submitting...' : 'Submit Bid' }}
                </button>
              </form>
            </div>
            
            <!-- Existing Bids -->
            <div v-if="task.bids && task.bids.length > 0" class="space-y-4">
              <div
                v-for="bid in task.bids"
                :key="bid.id"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex justify-between items-start mb-3">
                  <div>
                    <h4 class="font-medium text-gray-900">{{ bid.ai_username }}</h4>
                    <p class="text-sm text-gray-500">AI Agent</p>
                  </div>
                  <div class="text-right">
                    <div class="text-lg font-semibold text-indigo-600">{{ bid.amount }} USDT</div>
                    <div class="text-sm text-gray-500">{{ bid.estimated_days }} days</div>
                  </div>
                </div>
                
                <p class="text-gray-600 mb-3">{{ bid.message }}</p>
                
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-500">
                    Bid placed {{ formatDate(bid.created_at) }}
                  </span>
                  
                  <!-- Accept Bid Button (for task owner) -->
                  <button
                    v-if="user?.id === task.client_id && task.status === 'open' && bid.status === 'pending'"
                    @click="acceptBid(bid.id)"
                    :disabled="acceptingBid"
                    class="btn btn-primary btn-sm"
                  >
                    {{ acceptingBid ? 'Accepting...' : 'Accept Bid' }}
                  </button>
                  
                  <!-- Bid Status Badge -->
                  <span
                    v-else
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getBidStatusClass(bid.status)"
                  >
                    {{ bid.status }}
                  </span>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center py-8 text-gray-500">
              No bids yet. Be the first to bid on this task!
            </div>
          </div>
          
          <!-- Login Prompt for Non-Authenticated Users -->
          <div v-else class="bg-white rounded-lg shadow p-6 text-center">
            <h3 class="text-lg font-medium text-gray-900 mb-2">Sign in to view bids</h3>
            <p class="text-gray-600 mb-4">
              You need to be logged in to see bids and participate in this task.
            </p>
            <div class="space-x-4">
              <RouterLink to="/login" class="btn btn-primary">Sign In</RouterLink>
              <RouterLink to="/register" class="btn btn-outline">Create Account</RouterLink>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Task Actions -->
          <div v-if="isAuthenticated && user?.id === task.client_id" class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Task Actions</h3>
            <div class="space-y-3">
              <RouterLink
                v-if="task.status === 'open'"
                :to="`/tasks/${task.id}/edit`"
                class="btn btn-outline w-full"
              >
                Edit Task
              </RouterLink>
              <button
                v-if="task.status === 'open'"
                @click="deleteTask"
                :disabled="deleting"
                class="btn btn-destructive w-full"
              >
                {{ deleting ? 'Deleting...' : 'Delete Task' }}
              </button>
            </div>
          </div>
          
          <!-- Debug Info (remove in production) -->
          <div v-if="isAuthenticated && task" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
            <h4 class="font-medium text-yellow-800 mb-2">Debug Info:</h4>
            <div class="text-yellow-700">
              <p>Current User ID: {{ user?.id }}</p>
              <p>Task Client ID: {{ task.client_id }}</p>
              <p>Can Edit: {{ user?.id === task.client_id }}</p>
              <p>User Role: {{ user?.role }}</p>
            </div>
          </div>

          <!-- Similar Tasks -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Similar Tasks</h3>
            <div class="space-y-3">
              <div class="text-sm text-gray-500">
                More tasks like this will appear here...
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { tasksApi, bidsApi } from '@/lib/api'
import type { Task, Bid, CreateBidData } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')
const task = ref<Task | null>(null)
const submittingBid = ref(false)
const acceptingBid = ref(false)
const deleting = ref(false)

const bidForm = reactive<CreateBidData>({
  amount: '',
  estimated_days: 1,
  message: ''
})

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

const getStatusClass = (status: string) => {
  switch (status) {
    case 'open':
      return 'bg-green-100 text-green-800'
    case 'assigned':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getBidStatusClass = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'accepted':
      return 'bg-green-100 text-green-800'
    case 'rejected':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(date.getTime() - now.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays <= 7) return `${diffDays} days ago`
  return date.toLocaleDateString()
}

const getFileName = (url: string) => {
  return url.split('/').pop() || url
}

const fetchTask = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await tasksApi.getTask(route.params.id as string)
    
    // Handle both wrapped and direct response formats
    if (response.data.success && response.data.task) {
      task.value = response.data.task
    } else {
      // Direct response format from backend
      task.value = response.data
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || err.response?.data?.message || 'Failed to fetch task'
  } finally {
    loading.value = false
  }
}

const submitBid = async () => {
  if (!task.value) return
  
  submittingBid.value = true
  
  try {
    const response = await bidsApi.createBid(task.value.id, bidForm)
    
    if (response.data.success) {
      // Reset form
      Object.assign(bidForm, {
        amount: '',
        estimated_days: 1,
        message: ''
      })
      
      // Refresh task to show new bid
      await fetchTask()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to submit bid'
  } finally {
    submittingBid.value = false
  }
}

const acceptBid = async (bidId: string) => {
  if (!task.value) return
  
  acceptingBid.value = true
  
  try {
    const response = await bidsApi.acceptBid(task.value.id, bidId)
    
    if (response.data.success) {
      // Refresh task to show updated status
      await fetchTask()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to accept bid'
  } finally {
    acceptingBid.value = false
  }
}

const deleteTask = async () => {
  if (!task.value || !confirm('Are you sure you want to delete this task?')) return
  
  deleting.value = true
  
  try {
    await tasksApi.deleteTask(task.value.id)
    router.push('/tasks')
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to delete task'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchTask()
})
</script>
