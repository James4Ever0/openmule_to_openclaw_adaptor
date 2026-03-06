<template>
  <div class="task-create-container">
    <div class="max-w-4xl mx-auto p-6">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Create New Task</h1>
      
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

        <!-- File Attachments -->
        <div>
          <FileUpload 
            :direct-attach="true"
            ref="fileUploadComponent"
          />
        </div>

        <!-- Legacy Attachments (Hidden for compatibility) -->
        <input type="hidden" v-model="form.attachments" />

        <!-- Error Message -->
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {{ error }}
        </div>

        <!-- Success Message -->
        <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {{ success }}
        </div>

        <!-- Submit Button -->
        <div class="flex justify-end space-x-4">
          <button
            type="button"
            @click="$router.push('/tasks')"
            class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Creating...' : 'Create Task' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { tasksApi } from '@/lib/api'
import FileUpload from '@/components/FileUpload.vue'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  title: '',
  description: '',
  budget: '',
  deadline: '',
  category: '',
  attachments: []
})

const attachmentsText = ref('')
const fileUploadComponent = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref('')

// Minimum datetime for deadline (current time)
const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

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

const handleFilesAddedToTask = (fileIds) => {
  // This is called when files are added to a task (for existing tasks)
  // For new tasks, we'll handle this differently
  console.log('Files added to task:', fileIds)
}

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    console.log('Submitting form...') // Debug log

    const response = await tasksApi.createTask(form.value)

    if (!response.data.success) {
      throw new Error(response.data.error?.message || 'Failed to create task')
    }

    const data = response.data.data
    success.value = 'Task created successfully!'
    
    // Redirect to task detail page after a short delay
    setTimeout(() => {
      router.push(`/tasks/${data.id}`)
    }, 1500)

  } catch (err) {
    error.value = err.message || 'An error occurred while creating the task'
  } finally {
    loading.value = false
  }
}

// Component is already protected by router guard
onMounted(() => {
  // Authentication is handled by router guard
})
</script>

<style scoped>
.task-create-container {
  min-height: calc(100vh - 64px);
  background-color: #f9fafb;
}
</style>