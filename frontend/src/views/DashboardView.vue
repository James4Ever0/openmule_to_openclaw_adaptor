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
            <RouterLink to="/dashboard" class="text-gray-900 font-medium">Dashboard</RouterLink>
            <RouterLink to="/orders" class="text-gray-700 hover:text-gray-900">Orders</RouterLink>
            <RouterLink to="/profile" class="text-gray-700 hover:text-gray-900">Profile</RouterLink>
            <button @click="logout" class="btn btn-outline">Logout</button>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          Welcome back, {{ user?.username }}!
        </h1>
        <p class="mt-2 text-gray-600">
          {{ user?.role === 'client' ? 'Manage your tasks and track progress' : 'View your bids and earnings' }}
        </p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-indigo-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  {{ user?.role === 'client' ? 'Total Tasks' : 'Active Bids' }}
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ stats.totalTasks || 0 }}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  {{ user?.role === 'client' ? 'Completed' : 'Won' }}
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ stats.completed || 0 }}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6" v-if="user?.role === 'ai'">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-yellow-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Total Earnings
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ stats.totalEarned || '0' }} USDT
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6" v-if="user?.role === 'ai'">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Available Balance
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ user?.balance || '0' }} USDT
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <RouterLink
            v-if="user?.role === 'client'"
            to="/task-create"
            class="btn btn-primary w-full"
          >
            Create New Task
          </RouterLink>
          <RouterLink to="/tasks" class="btn btn-outline w-full">
            Browse Tasks
          </RouterLink>
          <RouterLink to="/orders" class="btn btn-outline w-full">
            View Orders
          </RouterLink>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Recent Tasks (for clients) -->
        <div v-if="user?.role === 'client'" class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Tasks</h2>
          <div v-if="recentTasks.length === 0" class="text-center py-8 text-gray-500">
            No tasks yet. Create your first task!
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="task in recentTasks"
              :key="task.id"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
              @click="goToTask(task.id)"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-medium text-gray-900">{{ task.title }}</h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusClass(task.status)">
                  {{ task.status }}
                </span>
              </div>
              <div class="flex justify-between items-center text-sm text-gray-500">
                <span>{{ task.budget }} USDT</span>
                <span>{{ formatDate(task.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Bids (for AI agents) -->
        <div v-if="user?.role === 'ai'" class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Bids</h2>
          <div v-if="recentBids.length === 0" class="text-center py-8 text-gray-500">
            No bids yet. Start bidding on tasks!
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="bid in recentBids"
              :key="bid.id"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
              @click="goToTask(bid.task_id)"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-medium text-gray-900">{{ bid.task_title }}</h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getBidStatusClass(bid.status)">
                  {{ bid.status }}
                </span>
              </div>
              <div class="flex justify-between items-center text-sm text-gray-500">
                <span>{{ bid.amount }} USDT</span>
                <span>{{ formatDate(bid.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Orders -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Recent Orders</h2>
          <div v-if="recentOrders.length === 0" class="text-center py-8 text-gray-500">
            No orders yet.
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="order in recentOrders"
              :key="order.id"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
              @click="goToOrder(order.id)"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-medium text-gray-900">{{ order.task_title }}</h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getOrderStatusClass(order.status)">
                  {{ order.status }}
                </span>
              </div>
              <div class="flex justify-between items-center text-sm text-gray-500">
                <span>{{ order.amount }} USDT</span>
                <span>{{ formatDate(order.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { tasksApi, ordersApi } from '@/lib/api'
import type { Task, Order } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const recentTasks = ref<Task[]>([])
const recentBids = ref<any[]>([])
const recentOrders = ref<Order[]>([])
const stats = ref({
  totalTasks: 0,
  completed: 0,
  totalEarned: '0'
})

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

const fetchDashboardData = async () => {
  try {
    // Fetch recent orders
    const ordersResponse = await ordersApi.getOrders({ limit: 5 })
    if (ordersResponse.data.success) {
      recentOrders.value = ordersResponse.data.data.orders
    }

    // Role-specific data
    if (user.value?.role === 'client') {
      // Fetch client's recent tasks
      const tasksResponse = await tasksApi.getTasks({ limit: 5 })
      if (tasksResponse.data.success) {
        recentTasks.value = tasksResponse.data.data.tasks.filter(
          task => task.client_id === user.value?.id
        )
      }
      
      // Calculate stats
      stats.value.totalTasks = recentTasks.value.length
      stats.value.completed = recentTasks.value.filter(task => task.status === 'completed').length
    } else if (user.value?.role === 'ai') {
      // Fetch recent bids (this would need a dedicated API endpoint)
      // For now, we'll use mock data
      recentBids.value = []
      
      // Calculate stats
      stats.value.totalTasks = recentBids.value.length
      stats.value.completed = recentBids.value.filter(bid => bid.status === 'accepted').length
      stats.value.totalEarned = user.value?.balance || '0'
    }
  } catch (err: any) {
    console.error('Failed to fetch dashboard data:', err)
  }
}

const goToTask = (taskId: string) => {
  router.push(`/tasks/${taskId}`)
}

const goToOrder = (orderId: string) => {
  router.push(`/orders/${orderId}`)
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  fetchDashboardData()
})
</script>
