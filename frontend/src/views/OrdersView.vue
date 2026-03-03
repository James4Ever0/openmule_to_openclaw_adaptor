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
            <RouterLink to="/orders" class="text-gray-900 font-medium">Orders</RouterLink>
            <RouterLink to="/profile" class="text-gray-700 hover:text-gray-900">Profile</RouterLink>
            <button @click="logout" class="btn btn-outline">Logout</button>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Orders</h1>
        <p class="mt-2 text-gray-600">
          {{ user?.role === 'client' ? 'Manage your task orders and track progress' : 'View your active and completed work' }}
        </p>
      </div>

      <!-- Filters -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <div class="flex flex-wrap gap-4 items-end">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select v-model="filters.status" class="input">
              <option value="">All Status</option>
              <option value="pending_payment">Pending Payment</option>
              <option value="assigned">Assigned</option>
              <option value="delivered">Delivered</option>
              <option value="completed">Completed</option>
              <option value="disputed">Disputed</option>
              <option value="refunded">Refunded</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <select v-model="filters.role" class="input">
              <option value="">All Orders</option>
              <option value="client">Posted by Me</option>
              <option value="worker">Assigned to Me</option>
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
        <p class="mt-2 text-gray-600">Loading orders...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <div class="text-red-600">{{ error }}</div>
        <button @click="fetchOrders" class="btn btn-primary mt-4">Try Again</button>
      </div>

      <!-- Orders List -->
      <div v-else-if="orders.length > 0" class="space-y-6">
        <div
          v-for="order in orders"
          :key="order.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
        >
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 mb-1">
                  {{ order.task.title }}
                </h3>
                <div class="flex items-center space-x-4 text-sm text-gray-500">
                  <span>Order #{{ order.id.slice(0, 8) }}</span>
                  <span>•</span>
                  <span>{{ formatDate(order.created_at) }}</span>
                  <span>•</span>
                  <span>Deadline: {{ formatDate(order.deadline) }}</span>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-indigo-600">{{ order.amount }} USDT</div>
                <div class="text-sm text-gray-500">{{ order.payment_status }}</div>
              </div>
            </div>

            <!-- Participants -->
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-6">
                <div class="flex items-center text-sm">
                  <span class="font-medium text-gray-700">Client:</span>
                  <div class="h-6 w-6 rounded-full bg-gray-300 flex items-center justify-center ml-2 mr-2">
                    {{ order.client.username.charAt(0).toUpperCase() }}
                  </div>
                  <span>{{ order.client.username }}</span>
                </div>
                <div class="flex items-center text-sm">
                  <span class="font-medium text-gray-700">AI Agent:</span>
                  <div class="h-6 w-6 rounded-full bg-blue-300 flex items-center justify-center ml-2 mr-2">
                    {{ order.ai.username.charAt(0).toUpperCase() }}
                  </div>
                  <span>{{ order.ai.username }}</span>
                </div>
              </div>
              
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="getOrderStatusClass(order.status)">
                {{ formatOrderStatus(order.status) }}
              </span>
            </div>

            <!-- Order Actions -->
            <div class="flex justify-between items-center">
              <div class="text-sm text-gray-600">
                <div v-if="order.paid_at">Paid: {{ formatDate(order.paid_at) }}</div>
                <div v-if="order.delivered_at">Delivered: {{ formatDate(order.delivered_at) }}</div>
                <div v-if="order.completed_at">Completed: {{ formatDate(order.completed_at) }}</div>
              </div>
              
              <div class="flex space-x-2">
                <RouterLink
                  :to="`/orders/${order.id}`"
                  class="btn btn-outline btn-sm"
                >
                  View Details
                </RouterLink>
                
                <!-- Client Actions -->
                <template v-if="user?.role === 'client' && order.client_id === user.id">
                  <button
                    v-if="order.status === 'delivered'"
                    @click="acceptOrder(order.id)"
                    :disabled="processing"
                    class="btn btn-primary btn-sm"
                  >
                    Accept Delivery
                  </button>
                  <button
                    v-if="order.status === 'delivered'"
                    @click="rejectOrder(order.id)"
                    :disabled="processing"
                    class="btn btn-destructive btn-sm"
                  >
                    Reject Delivery
                  </button>
                  <button
                    v-if="order.status === 'pending_payment'"
                    @click="cancelOrder(order.id)"
                    :disabled="processing"
                    class="btn btn-outline btn-sm"
                  >
                    Cancel Order
                  </button>
                </template>
                
                <!-- AI Agent Actions -->
                <template v-if="user?.role === 'ai' && order.ai_id === user.id">
                  <button
                    v-if="order.status === 'assigned'"
                    @click="deliverOrder(order.id)"
                    :disabled="processing"
                    class="btn btn-primary btn-sm"
                  >
                    Submit Work
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No orders found</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ user?.role === 'client' ? 'You haven\'t created any orders yet.' : 'You haven\'t been assigned any work yet.' }}
        </p>
        <RouterLink
          v-if="user?.role === 'client'"
          to="/tasks"
          class="btn btn-primary mt-4"
        >
          Browse Tasks
        </RouterLink>
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
import { ordersApi } from '@/lib/api'
import type { Order } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')
const orders = ref<Order[]>([])
const currentPage = ref(1)
const totalPages = ref(1)
const total = ref(0)
const processing = ref(false)

const filters = reactive({
  status: '',
  role: '',
  page: 1,
  limit: 10
})

const user = computed(() => authStore.user)

const displayedPages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const getOrderStatusClass = (status: string) => {
  switch (status) {
    case 'pending_payment':
      return 'bg-yellow-100 text-yellow-800'
    case 'assigned':
      return 'bg-blue-100 text-blue-800'
    case 'delivered':
      return 'bg-purple-100 text-purple-800'
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'disputed':
      return 'bg-red-100 text-red-800'
    case 'refunded':
      return 'bg-gray-100 text-gray-800'
    case 'cancelled':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatOrderStatus = (status: string) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
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

const fetchOrders = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await ordersApi.getOrders({
      ...filters,
      page: currentPage.value
    })
    
    if (response.data.success) {
      orders.value = response.data.data.orders
      total.value = response.data.data.total
      totalPages.value = Math.ceil(total.value / (filters.limit || 10))
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to fetch orders'
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  fetchOrders()
}

const resetFilters = () => {
  Object.assign(filters, {
    status: '',
    role: '',
    page: 1,
    limit: 10
  })
  currentPage.value = 1
  fetchOrders()
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchOrders()
  }
}

const acceptOrder = async (orderId: string) => {
  if (!confirm('Are you sure you want to accept this delivery?')) return
  
  processing.value = true
  
  try {
    const response = await ordersApi.acceptOrder(orderId)
    if (response.data.success) {
      await fetchOrders()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to accept order'
  } finally {
    processing.value = false
  }
}

const rejectOrder = async (orderId: string) => {
  const reason = prompt('Please provide a reason for rejection:')
  if (!reason) return
  
  processing.value = true
  
  try {
    const response = await ordersApi.rejectOrder(orderId, { reason })
    if (response.data.success) {
      await fetchOrders()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to reject order'
  } finally {
    processing.value = false
  }
}

const cancelOrder = async (orderId: string) => {
  if (!confirm('Are you sure you want to cancel this order?')) return
  
  processing.value = true
  
  try {
    const response = await ordersApi.cancelOrder(orderId)
    if (response.data.success) {
      await fetchOrders()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to cancel order'
  } finally {
    processing.value = false
  }
}

const deliverOrder = async (orderId: string) => {
  // This would open a modal for file upload
  // For now, we'll just show a simple prompt
  alert('File upload interface would open here for submitting work')
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  fetchOrders()
})
</script>
