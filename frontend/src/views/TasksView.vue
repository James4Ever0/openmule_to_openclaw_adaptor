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
            <RouterLink to="/tasks" class="text-gray-900 font-medium">Browse Tasks</RouterLink>
            <template v-if="!isAuthenticated">
              <RouterLink to="/login" class="text-gray-700 hover:text-gray-900">Login</RouterLink>
              <RouterLink to="/register" class="btn btn-primary">Sign Up</RouterLink>
            </template>
            <template v-else>
              <RouterLink to="/dashboard" class="text-gray-700 hover:text-gray-900">Dashboard</RouterLink>
              <button @click="logout" class="btn btn-outline">Logout</button>
            </template>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Filters -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Filter Tasks</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select v-model="filters.status" class="input">
              <option value="">All Status</option>
              <option value="open">Open</option>
              <option value="assigned">Assigned</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select v-model="filters.category" class="input">
              <option value="">All Categories</option>
              <option value="web-dev">Web Development</option>
              <option value="design">Design</option>
              <option value="writing">Writing</option>
              <option value="data-analysis">Data Analysis</option>
              <option value="marketing">Marketing</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Min Budget (USDT)</label>
            <input
              v-model="filters.min_budget"
              type="number"
              placeholder="0"
              class="input"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Max Budget (USDT)</label>
            <input
              v-model="filters.max_budget"
              type="number"
              placeholder="1000"
              class="input"
            />
          </div>
        </div>
        
        <div class="flex justify-between items-center mt-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
            <select v-model="filters.sort" class="input">
              <option value="new">Newest First</option>
              <option value="budget_desc">Highest Budget</option>
              <option value="budget_asc">Lowest Budget</option>
            </select>
          </div>
          
          <div class="flex space-x-2">
            <button @click="applyFilters" class="btn btn-primary">Apply Filters</button>
            <button @click="resetFilters" class="btn btn-outline">Reset</button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p class="mt-2 text-gray-600">Loading tasks...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <div class="text-red-600">{{ error }}</div>
        <button @click="fetchTasks" class="btn btn-primary mt-4">Try Again</button>
      </div>

      <!-- Tasks List -->
      <div v-else-if="tasks.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
          @click="goToTask(task.id)"
        >
          <div class="p-6">
            <div class="flex justify-between items-start mb-2">
              <h3 class="text-lg font-semibold text-gray-900 line-clamp-2">
                {{ task.title }}
              </h3>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusClass(task.status)">
                {{ task.status }}
              </span>
            </div>
            
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">
              {{ task.description }}
            </p>
            
            <div class="flex items-center justify-between text-sm">
              <div>
                <span class="font-medium text-indigo-600">{{ task.budget }} USDT</span>
                <span class="text-gray-500 ml-2">• {{ task.bid_count || 0 }} bids</span>
              </div>
              <div class="text-gray-500">
                <div class="flex items-center">
                  <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ formatDate(task.deadline) }}
                </div>
              </div>
            </div>
            
            <div class="mt-4 flex items-center justify-between">
              <div class="flex items-center text-sm text-gray-500">
                <div class="h-6 w-6 rounded-full bg-gray-300 flex items-center justify-center mr-2">
                  {{ task.client?.username?.charAt(0).toUpperCase() }}
                </div>
                {{ task.client?.username }}
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                {{ task.category }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No tasks found</h3>
        <p class="mt-1 text-sm text-gray-500">
          Try adjusting your filters or check back later for new tasks.
        </p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-8 flex justify-center">
        <nav class="flex items-center space-x-2">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="btn btn-outline btn-sm"
          >
            Previous
          </button>
          
          <div class="flex space-x-1">
            <button
              v-for="page in displayedPages"
              :key="page"
              @click="goToPage(page)"
              :class="page === currentPage ? 'btn btn-primary btn-sm' : 'btn btn-outline btn-sm'"
            >
              {{ page }}
            </button>
          </div>
          
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
            class="btn btn-outline btn-sm"
          >
            Next
          </button>
        </nav>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { tasksApi } from '@/lib/api'
import type { Task, TaskFilters } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')
const tasks = ref<Task[]>([])
const currentPage = ref(1)
const totalPages = ref(1)
const total = ref(0)

const filters = reactive<TaskFilters>({
  status: '',
  category: '',
  min_budget: '',
  max_budget: '',
  sort: 'new',
  page: 1,
  limit: 12
})

const isAuthenticated = computed(() => authStore.isAuthenticated)

const displayedPages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

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

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(date.getTime() - now.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Tomorrow'
  if (diffDays <= 7) return `${diffDays} days`
  return date.toLocaleDateString()
}

const fetchTasks = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await tasksApi.getTasks({
      ...filters,
      page: currentPage.value
    })
    
    if (response.data.success) {
      tasks.value = response.data.data.tasks
      total.value = response.data.data.total
      totalPages.value = Math.ceil(total.value / (filters.limit || 12))
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to fetch tasks'
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  fetchTasks()
}

const resetFilters = () => {
  Object.assign(filters, {
    status: '',
    category: '',
    min_budget: '',
    max_budget: '',
    sort: 'new',
    page: 1,
    limit: 12
  })
  currentPage.value = 1
  fetchTasks()
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchTasks()
  }
}

const goToTask = (taskId: string) => {
  router.push(`/tasks/${taskId}`)
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
