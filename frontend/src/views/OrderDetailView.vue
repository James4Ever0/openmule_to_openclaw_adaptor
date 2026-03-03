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
            <RouterLink to="/profile" class="text-gray-700 hover:text-gray-900">Profile</RouterLink>
            <button @click="logout" class="btn btn-outline">Logout</button>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p class="mt-2 text-gray-600">Loading order details...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <div class="text-red-600">{{ error }}</div>
        <button @click="fetchOrder" class="btn btn-primary mt-4">Try Again</button>
      </div>

      <!-- Order Details -->
      <div v-else-if="order" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Order Header -->
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex justify-between items-start mb-4">
              <h1 class="text-2xl font-bold text-gray-900">{{ order.task.title }}</h1>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="getOrderStatusClass(order.status)">
                {{ formatOrderStatus(order.status) }}
              </span>
            </div>
            
            <div class="flex items-center space-x-4 text-sm text-gray-500 mb-4">
              <span>Order #{{ order.id.slice(0, 8) }}</span>
              <span>•</span>
              <span>Created {{ formatDate(order.created_at) }}</span>
              <span>•</span>
              <span>Deadline: {{ formatDate(order.deadline) }}</span>
            </div>
            
            <div class="flex items-center justify-between mb-4">
              <div>
                <span class="text-3xl font-bold text-indigo-600">{{ order.amount }} USDT</span>
                <span class="ml-2 text-gray-500">total amount</span>
              </div>
              <div class="text-right">
                <div class="text-sm text-gray-500">Payment Status</div>
                <div class="font-medium" :class="getPaymentStatusClass(order.payment_status)">
                  {{ formatPaymentStatus(order.payment_status) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Task Description -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Task Description</h2>
            <div class="prose max-w-none text-gray-600">
              <p>{{ order.task.description }}</p>
            </div>
          </div>

          <!-- Deliverables -->
          <div v-if="order.deliverables && order.deliverables.length > 0" class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Deliverables</h2>
            <div class="space-y-4">
              <div
                v-for="deliverable in order.deliverables"
                :key="deliverable.id"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex justify-between items-start mb-2">
                  <h3 class="font-medium text-gray-900">Deliverable #{{ deliverable.id.slice(0, 8) }}</h3>
                  <span class="text-sm text-gray-500">
                    {{ formatDate(deliverable.created_at) }}
                  </span>
                </div>
                
                <p v-if="deliverable.description" class="text-gray-600 mb-3">
                  {{ deliverable.description }}
                </p>
                
                <a
                  :href="deliverable.file_url"
                  target="_blank"
                  class="flex items-center p-3 border border-gray-200 rounded-md hover:bg-gray-50"
                >
                  <svg class="h-5 w-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  <span class="text-sm text-gray-600">{{ getFileName(deliverable.file_url) }}</span>
                </a>
              </div>
            </div>
          </div>

          <!-- Messages -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Messages</h2>
            
            <!-- Message Form -->
            <div class="mb-6 p-4 bg-gray-50 rounded-lg">
              <form @submit.prevent="sendMessage" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
                  <textarea
                    v-model="messageForm.content"
                    rows="3"
                    required
                    class="input"
                    placeholder="Type your message..."
                  ></textarea>
                </div>
                
                <button
                  type="submit"
                  :disabled="sendingMessage"
                  class="btn btn-primary"
                >
                  {{ sendingMessage ? 'Sending...' : 'Send Message' }}
                </button>
              </form>
            </div>
            
            <!-- Messages List -->
            <div v-if="messages.length > 0" class="space-y-4 max-h-96 overflow-y-auto">
              <div
                v-for="message in messages"
                :key="message.id"
                class="flex"
                :class="message.sender_id === user?.id ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-xs lg:max-w-md"
                  :class="message.sender_id === user?.id ? 'order-2' : 'order-1'"
                >
                  <div class="flex items-center space-x-2 mb-1">
                    <div class="h-6 w-6 rounded-full bg-gray-300 flex items-center justify-center text-xs">
                      {{ message.sender_type === 'client' ? 'C' : 'AI' }}
                    </div>
                    <span class="text-xs text-gray-500">
                      {{ formatDate(message.created_at) }}
                    </span>
                  </div>
                  <div
                    class="rounded-lg px-4 py-2"
                    :class="message.sender_id === user?.id ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-900'"
                  >
                    <p class="text-sm">{{ message.content }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center py-8 text-gray-500">
              No messages yet. Start the conversation!
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Participants -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Participants</h3>
            <div class="space-y-4">
              <div class="flex items-center space-x-3">
                <div class="h-8 w-8 rounded-full bg-blue-300 flex items-center justify-center text-sm">
                  {{ order.client.username.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <div class="font-medium text-gray-900">{{ order.client.username }}</div>
                  <div class="text-sm text-gray-500">Client</div>
                </div>
              </div>
              
              <div class="flex items-center space-x-3">
                <div class="h-8 w-8 rounded-full bg-green-300 flex items-center justify-center text-sm">
                  {{ order.ai.username.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <div class="font-medium text-gray-900">{{ order.ai.username }}</div>
                  <div class="text-sm text-gray-500">AI Agent</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Order Actions -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Actions</h3>
            <div class="space-y-3">
              <!-- Client Actions -->
              <template v-if="user?.role === 'client' && order.client_id === user.id">
                <button
                  v-if="order.status === 'pending_payment'"
                  @click="payOrder"
                  :disabled="processing"
                  class="btn btn-primary w-full"
                >
                  {{ processing ? 'Processing...' : 'Pay for Order' }}
                </button>
                
                <button
                  v-if="order.status === 'delivered'"
                  @click="acceptOrder"
                  :disabled="processing"
                  class="btn btn-primary w-full"
                >
                  {{ processing ? 'Processing...' : 'Accept Delivery' }}
                </button>
                
                <button
                  v-if="order.status === 'delivered'"
                  @click="rejectOrder"
                  :disabled="processing"
                  class="btn btn-destructive w-full"
                >
                  {{ processing ? 'Processing...' : 'Reject Delivery' }}
                </button>
                
                <button
                  v-if="order.status === 'pending_payment'"
                  @click="cancelOrder"
                  :disabled="processing"
                  class="btn btn-outline w-full"
                >
                  {{ processing ? 'Processing...' : 'Cancel Order' }}
                </button>
              </template>
              
              <!-- AI Agent Actions -->
              <template v-if="user?.role === 'ai' && order.ai_id === user.id">
                <button
                  v-if="order.status === 'assigned'"
                  @click="deliverOrder"
                  :disabled="processing"
                  class="btn btn-primary w-full"
                >
                  {{ processing ? 'Processing...' : 'Submit Work' }}
                </button>
              </template>
              
              <!-- Common Actions -->
              <button
                v-if="order.status === 'assigned' || order.status === 'delivered'"
                @click="openDispute"
                :disabled="processing"
                class="btn btn-outline w-full"
              >
                {{ processing ? 'Processing...' : 'Open Dispute' }}
              </button>
            </div>
          </div>

          <!-- Order Timeline -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Timeline</h3>
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <div class="h-2 w-2 rounded-full bg-indigo-600 mt-2"></div>
                <div>
                  <div class="text-sm font-medium text-gray-900">Order Created</div>
                  <div class="text-xs text-gray-500">{{ formatDate(order.created_at) }}</div>
                </div>
              </div>
              
              <div v-if="order.paid_at" class="flex items-start space-x-3">
                <div class="h-2 w-2 rounded-full bg-green-600 mt-2"></div>
                <div>
                  <div class="text-sm font-medium text-gray-900">Payment Confirmed</div>
                  <div class="text-xs text-gray-500">{{ formatDate(order.paid_at) }}</div>
                </div>
              </div>
              
              <div v-if="order.delivered_at" class="flex items-start space-x-3">
                <div class="h-2 w-2 rounded-full bg-purple-600 mt-2"></div>
                <div>
                  <div class="text-sm font-medium text-gray-900">Work Delivered</div>
                  <div class="text-xs text-gray-500">{{ formatDate(order.delivered_at) }}</div>
                </div>
              </div>
              
              <div v-if="order.completed_at" class="flex items-start space-x-3">
                <div class="h-2 w-2 rounded-full bg-green-600 mt-2"></div>
                <div>
                  <div class="text-sm font-medium text-gray-900">Order Completed</div>
                  <div class="text-xs text-gray-500">{{ formatDate(order.completed_at) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ordersApi, messagesApi } from '@/lib/api'
import { useWebSocket } from '@/lib/websocket'
import type { Order, Message } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')
const order = ref<Order | null>(null)
const messages = ref<Message[]>([])
const processing = ref(false)
const sendingMessage = ref(false)

const messageForm = reactive({
  content: ''
})

const user = computed(() => authStore.user)

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

const getPaymentStatusClass = (status: string) => {
  switch (status) {
    case 'paid':
      return 'text-green-600'
    case 'unpaid':
      return 'text-yellow-600'
    case 'refunded':
      return 'text-red-600'
    default:
      return 'text-gray-600'
  }
}

const formatOrderStatus = (status: string) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatPaymentStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
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

const fetchOrder = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await ordersApi.getOrder(route.params.id as string)
    
    if (response.data.success) {
      order.value = response.data.order
      // Fetch messages after order is loaded
      await fetchMessages()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to fetch order'
  } finally {
    loading.value = false
  }
}

const fetchMessages = async () => {
  if (!order.value) return
  
  try {
    const response = await messagesApi.getMessages(order.value.id)
    if (response.data.success) {
      messages.value = response.data.messages
    }
  } catch (err: any) {
    console.error('Failed to fetch messages:', err)
  }
}

const sendMessage = async () => {
  if (!order.value || !messageForm.content.trim()) return
  
  sendingMessage.value = true
  
  try {
    // Send via WebSocket for real-time delivery
    send({
      type: 'message',
      content: messageForm.content
    })
    
    // Also save via API as backup
    const response = await messagesApi.sendMessage(order.value.id, {
      content: messageForm.content
    })
    
    if (response.data.success) {
      messageForm.content = ''
      // Message will be added via WebSocket handler
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to send message'
  } finally {
    sendingMessage.value = false
  }
}

const payOrder = async () => {
  if (!order.value) return
  
  processing.value = true
  
  try {
    const response = await ordersApi.payOrder(order.value.id)
    if (response.data.success) {
      // Show payment details
      alert(`Payment address: ${response.data.payment_address}\nAmount: ${response.data.amount} USDT\nExpires: ${response.data.expires_at}`)
      await fetchOrder()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to process payment'
  } finally {
    processing.value = false
  }
}

const acceptOrder = async () => {
  if (!order.value || !confirm('Are you sure you want to accept this delivery?')) return
  
  processing.value = true
  
  try {
    const response = await ordersApi.acceptOrder(order.value.id)
    if (response.data.success) {
      await fetchOrder()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to accept order'
  } finally {
    processing.value = false
  }
}

const rejectOrder = async () => {
  if (!order.value) return
  
  const reason = prompt('Please provide a reason for rejection:')
  if (!reason) return
  
  processing.value = true
  
  try {
    const response = await ordersApi.rejectOrder(order.value.id, { reason })
    if (response.data.success) {
      await fetchOrder()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to reject order'
  } finally {
    processing.value = false
  }
}

const cancelOrder = async () => {
  if (!order.value || !confirm('Are you sure you want to cancel this order?')) return
  
  processing.value = true
  
  try {
    const response = await ordersApi.cancelOrder(order.value.id)
    if (response.data.success) {
      await fetchOrder()
    }
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to cancel order'
  } finally {
    processing.value = false
  }
}

const deliverOrder = async () => {
  if (!order.value) return
  
  // This would open a file upload modal
  alert('File upload interface would open here for submitting deliverables')
}

const openDispute = async () => {
  if (!order.value) return
  
  const reason = prompt('Please describe the issue:')
  const details = prompt('Please provide more details about the dispute:')
  
  if (!reason || !details) return
  
  processing.value = true
  
  try {
    // This would call dispute API
    alert('Dispute functionality would be implemented here')
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to open dispute'
  } finally {
    processing.value = false
  }
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

// WebSocket setup
const { connect, disconnect, send, onMessage, isConnected } = useWebSocket(route.params.id as string)

onMounted(async () => {
  await fetchOrder()
  
  // Connect to WebSocket for real-time messaging
  await connect()
  
  // Set up message handler
  onMessage('message', (message) => {
    if (message.type === 'message') {
      messages.value.push(message)
    }
  })
})

onUnmounted(() => {
  disconnect()
})
</script>
