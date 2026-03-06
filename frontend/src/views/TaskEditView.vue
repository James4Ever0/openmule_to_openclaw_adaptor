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

    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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

      <!-- Edit Form -->
      <div v-else-if="task" class="bg-white rounded-lg shadow p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">Edit Task</h1>
        
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Title -->
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
              Task Title *
            </label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter task title"
            />
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              id="description"
              v-model="form.description"
              required
              rows="6"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe your task in detail"
            ></textarea>
          </div>

          <!-- Category -->
          <div>
            <label for="category" class="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <select
              id="category"
              v-model="form.category"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a category</option>
              <option value="development">Development</option>
              <option value="design">Design</option>
              <option value="writing">Writing</option>
              <option value="marketing">Marketing</option>
              <option value="data">Data & Analytics</option>
              <option value="other">Other</option>
            </select>
          </div>

          <!-- Budget -->
          <div>
            <label for="budget" class="block text-sm font-medium text-gray-700 mb-2">
              Budget (USDT) *
            </label>
            <input
              id="budget"
              v-model="form.budget"
              type="text"
              required
              pattern="[0-9]+(\.[0-9]{1,2})?"
              @input="handleBudgetInput"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter budget amount"
            />
          </div>

          <!-- Deadline -->
          <div>
            <label for="deadline" class="block text-sm font-medium text-gray-700 mb-2">
              Deadline *
            </label>
            <input
              id="deadline"
              v-model="form.deadline"
              type="datetime-local"
              required
              :min="minDateTime"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- Attachments -->
          <div>
            <label for="attachments" class="block text-sm font-medium text-gray-700 mb-2">
              Attachments (URLs, one per line)
            </label>
            <textarea
              id="attachments"
              v-model="attachmentsText"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com/file1.pdf&#10;https://example.com/file2.jpg"
            ></textarea>
          </div>

          <!-- Error Message -->
          <div v-if="submitError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {{ submitError }}
          </div>

          <!-- Success Message -->
          <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
            {{ success }}
          </div>

          <!-- Submit Buttons -->
          <div class="flex justify-end space-x-4">
            <RouterLink
              :to="`/tasks/${task.id}`"
              class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </RouterLink>
            <button
              type="submit"
              :disabled="submitting"
              class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submitting ? 'Updating...' : 'Update Task' }}
            </button>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { tasksApi } from '@/lib/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const submitError = ref('')
const success = ref('')
const task = ref(null)

const form = ref({
  title: '',
  description: '',
  budget: '',
  deadline: '',
  category: '',
  attachments: []
})

const attachmentsText = ref('')

// Minimum datetime for deadline (current time)
const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

const handleBudgetInput = (event) => {
  // Only allow digits and one decimal point
  let value = event.target.value
  
  // Remove all non-digit and non-decimal point characters
  value = value.replace(/[^0-9.]/g, '')
  
  // Prevent first digit from being zero (unless it's 0.x)
  if (value.length > 1 && value[0] === '0' && value[1] !== '.') {
    value = value.substring(1)
  }
  
  // Ensure only one decimal point
  const parts = value.split('.')
  if (parts.length > 2) {
    value = parts[0] + '.' + parts.slice(1).join('')
  }
  
  // Limit decimal places to 2
  if (parts.length === 2 && parts[1].length > 2) {
    value = parts[0] + '.' + parts[1].substring(0, 2)
  }
  
  form.value.budget = value
}

const fetchTask = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await tasksApi.getTask(route.params.id)
    
    // Handle both wrapped and direct response formats
    let taskData
    if (response.data.success && response.data.task) {
      taskData = response.data.task
    } else {
      // Direct response format from backend
      taskData = response.data
    }
    
    task.value = taskData
    
    // Check if current user is the task owner
    if (user.value?.id !== taskData.client_id) {
      error.value = 'You are not authorized to edit this task'
      return
    }
    
    // Populate form with task data
    form.value = {
      title: taskData.title,
      description: taskData.description,
      budget: taskData.budget,
      deadline: taskData.deadline ? new Date(taskData.deadline).toISOString().slice(0, 16) : '',
      category: taskData.category,
      attachments: taskData.attachments || []
    }
    
    // Populate attachments text area
    if (taskData.attachments && taskData.attachments.length > 0) {
      attachmentsText.value = taskData.attachments.join('\n')
    }
    
  } catch (err) {
    error.value = err.response?.data?.error?.message || err.response?.data?.message || 'Failed to fetch task'
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  submitError.value = ''
  success.value = ''

  try {
    // Parse attachments from text area
    if (attachmentsText.value.trim()) {
      form.value.attachments = attachmentsText.value
        .split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0)
    } else {
      form.value.attachments = []
    }

    const response = await tasksApi.updateTask(task.value.id, form.value)

    success.value = 'Task updated successfully!'
    
    // Redirect to task detail page after a short delay
    setTimeout(() => {
      router.push(`/tasks/${task.value.id}`)
    }, 1500)

  } catch (err) {
    submitError.value = err.response?.data?.error?.message || err.response?.data?.message || 'Failed to update task'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchTask()
})
</script>
