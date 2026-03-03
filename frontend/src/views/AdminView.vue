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
            <RouterLink to="/admin" class="text-gray-900 font-medium">Admin Panel</RouterLink>
            <button @click="logout" class="btn btn-outline">Logout</button>
          </nav>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Admin Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Customer Service Admin Panel</h1>
        <p class="mt-2 text-gray-600">
          Manage refund requests and disputes for the OpenMule platform
        </p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-yellow-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m0-3l-3-3m3 3v4m0 4h-6" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Pending Refunds</dt>
                <dd class="text-lg font-medium text-gray-900">{{ stats.pendingRefunds }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-red-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.29 3.86L1.29 9c-.47.46-.29.77l2.58 2.29l2.58-2.29c.3-.31.47-.29.77.29l8.58 2.29c.3.31.47.29.77.29l2.58-2.29c.3-.31.47-.29.77-.29l8.58 2.29c.3.31.47.29.77.29l2.58-2.29" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Disputes</dt>
                <dd class="text-lg font-medium text-gray-900">{{ stats.activeDisputes }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4 4m6 2a9 9 0 11-18 0 9 9 0 0118 0" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Resolved Today</dt>
                <dd class="text-lg font-medium text-gray-900">{{ stats.resolvedToday }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7m0 4h4m-4 0h4" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Processed</dt>
                <dd class="text-lg font-medium text-gray-900">{{ stats.totalProcessed }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8" aria-label="Tabs">
            <button
              @click="activeTab = 'refunds'"
              :class="[
                activeTab === 'refunds'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
              class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
            >
              Refund Requests
            </button>
            <button
              @click="activeTab = 'disputes'"
              :class="[
                activeTab === 'disputes'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
              class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
            >
              Disputes
            </button>
          </nav>
        </div>
      </div>

      <!-- Refunds Tab -->
      <div v-if="activeTab === 'refunds'" class="space-y-6">
        <!-- Filters -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Filter Refunds</h2>
          <div class="flex flex-wrap gap-4 items-end">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select v-model="refundFilters.status" class="input">
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div class="flex space-x-2">
              <button @click="applyRefundFilters" class="btn btn-primary">Apply Filters</button>
              <button @click="resetRefundFilters" class="btn btn-outline">Reset</button>
            </div>
          </div>
        </div>

        <!-- Refunds List -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Refund Requests</h2>
          </div>
          
          <!-- Loading State -->
          <div v-if="loading.refunds" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p class="mt-2 text-gray-600">Loading refunds...</p>
          </div>

          <!-- Refunds List -->
          <div v-else-if="refunds.length > 0" class="divide-y divide-gray-200">
            <div
              v-for="refund in refunds"
              :key="refund.id"
              class="p-6 hover:bg-gray-50"
            >
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h3 class="text-lg font-medium text-gray-900">
                    Refund #{{ refund.id.slice(0, 8) }}
                  </h3>
                  <p class="text-sm text-gray-500">
                    {{ formatDate(refund.created_at) }}
                  </p>
                </div>
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                      :class="getRefundStatusClass(refund.status)">
                  {{ formatRefundStatus(refund.status) }}
                </span>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 class="text-sm font-medium text-gray-900 mb-2">Order Details</h4>
                  <div class="text-sm text-gray-600">
                    <p><strong>Task:</strong> {{ refund.task_title }}</p>
                    <p><strong>Amount:</strong> {{ refund.order_amount }} USDT</p>
                    <p><strong>Client:</strong> {{ refund.client_username }}</p>
                    <p><strong>AI Agent:</strong> {{ refund.ai_username }}</p>
                  </div>
                </div>
                <div>
                  <h4 class="text-sm font-medium text-gray-900 mb-2">Reason</h4>
                  <p class="text-sm text-gray-600">{{ refund.reason }}</p>
                </div>
              </div>

              <!-- Actions for pending refunds -->
              <div v-if="refund.status === 'pending'" class="flex space-x-3">
                <button
                  @click="approveRefund(refund.id)"
                  :disabled="processing.refund"
                  class="btn btn-primary"
                >
                  {{ processing.refund ? 'Processing...' : 'Approve' }}
                </button>
                <button
                  @click="rejectRefund(refund.id)"
                  :disabled="processing.refund"
                  class="btn btn-destructive"
                >
                  {{ processing.refund ? 'Processing...' : 'Reject' }}
                </button>
              </div>

              <!-- Resolution info -->
              <div v-else-if="refund.status !== 'pending'" class="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 class="text-sm font-medium text-gray-900 mb-2">Resolution</h4>
                <p class="text-sm text-gray-600">
                  <strong>Status:</strong> {{ formatRefundStatus(refund.status) }}
                </p>
                <p v-if="refund.updated_at" class="text-sm text-gray-600">
                  <strong>Processed:</strong> {{ formatDate(refund.updated_at) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2v2a2 2 0 002 2h2a2 2 0 002-2V9a2 2 0 00-2-2h-2" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No refund requests found</h3>
            <p class="mt-1 text-sm text-gray-500">
              No refund requests have been submitted yet.
            </p>
          </div>
        </div>
      </div>

      <!-- Disputes Tab -->
      <div v-if="activeTab === 'disputes'" class="space-y-6">
        <!-- Disputes List -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Active Disputes</h2>
          </div>
          
          <!-- Loading State -->
          <div v-if="loading.disputes" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p class="mt-2 text-gray-600">Loading disputes...</p>
          </div>

          <!-- Disputes List -->
          <div v-else-if="disputes.length > 0" class="divide-y divide-gray-200">
            <div
              v-for="dispute in disputes"
              :key="dispute.id"
              class="p-6 hover:bg-gray-50"
            >
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h3 class="text-lg font-medium text-gray-900">
                    Dispute #{{ dispute.id.slice(0, 8) }}
                  </h3>
                  <p class="text-sm text-gray-500">
                    {{ formatDate(dispute.created_at) }}
                  </p>
                </div>
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                      :class="getDisputeStatusClass(dispute.status)">
                  {{ formatDisputeStatus(dispute.status) }}
                </span>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 class="text-sm font-medium text-gray-900 mb-2">Dispute Details</h4>
                  <div class="text-sm text-gray-600">
                    <p><strong>Task:</strong> {{ dispute.task_title }}</p>
                    <p><strong>Amount:</strong> {{ dispute.order_amount }} USDT</p>
                    <p><strong>Initiated by:</strong> {{ dispute.initiator_type }} ({{ dispute.initiator_type === 'client' ? dispute.client_username : dispute.ai_username }})</p>
                    <p><strong>Reason:</strong> {{ dispute.reason }}</p>
                  </div>
                </div>
              </div>

              <!-- Actions for active disputes -->
              <div v-if="dispute.status === 'active'" class="flex space-x-3">
                <button
                  @click="openResolveDialog(dispute)"
                  :disabled="processing.dispute"
                  class="btn btn-primary"
                >
                  {{ processing.dispute ? 'Processing...' : 'Resolve Dispute' }}
                </button>
              </div>

              <!-- Resolution info -->
              <div v-else-if="dispute.status === 'resolved'" class="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 class="text-sm font-medium text-gray-900 mb-2">Resolution</h4>
                <div class="text-sm text-gray-600">
                  <p><strong>Resolution:</strong> {{ dispute.resolution }}</p>
                  <p v-if="dispute.notes"><strong>Notes:</strong> {{ dispute.notes }}</p>
                  <p><strong>Resolved:</strong> {{ formatDate(dispute.updated_at) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m0-3l-3-3m3 3v4m0 4h-6" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No active disputes</h3>
            <p class="mt-1 text-sm text-gray-500">
              No disputes are currently active.
            </p>
          </div>
        </div>
      </div>

      <!-- Resolve Dispute Dialog -->
      <div v-if="resolveDialog.show" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div class="flex min-h-full items-center justify-center p-4">
          <div class="relative bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:w-full sm:max-w-lg sm:scale-100">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Resolve Dispute
                  </h3>
                  
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Resolution</label>
                      <textarea
                        v-model="resolveDialog.resolution"
                        rows="3"
                        required
                        class="input"
                        placeholder="Describe the resolution..."
                      ></textarea>
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                      <textarea
                        v-model="resolveDialog.notes"
                        rows="4"
                        required
                        class="input"
                        placeholder="Additional notes about the resolution..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  @click="closeResolveDialog"
                  class="btn btn-outline"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  @click="resolveDispute"
                  :disabled="processing.dispute"
                  class="btn btn-primary"
                >
                  {{ processing.dispute ? 'Resolving...' : 'Resolve Dispute' }}
                </button>
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
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { csApi } from '@/lib/api'
import type { RefundRequest, Dispute } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref<'refunds' | 'disputes'>('refunds')
const loading = ref({ refunds: false, disputes: false })
const processing = ref({ refund: false, dispute: false })
const refunds = ref<RefundRequest[]>([])
const disputes = ref<Dispute[]>([])

const stats = ref({
  pendingRefunds: 0,
  activeDisputes: 0,
  resolvedToday: 0,
  totalProcessed: 0
})

const refundFilters = reactive({
  status: ''
})

const resolveDialog = reactive({
  show: false,
  disputeId: '',
  resolution: '',
  notes: ''
})

const user = computed(() => authStore.user)

const getRefundStatusClass = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'approved':
      return 'bg-green-100 text-green-800'
    case 'rejected':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getDisputeStatusClass = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-red-100 text-red-800'
    case 'resolved':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatRefundStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDisputeStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const fetchRefunds = async () => {
  loading.value.refunds = true
  
  try {
    const response = await csApi.getRefundRequests(refundFilters)
    if (response.data.success) {
      refunds.value = response.data.data.refunds
      stats.value.pendingRefunds = refunds.value.filter(r => r.status === 'pending').length
    }
  } catch (err: any) {
    console.error('Failed to fetch refunds:', err)
  } finally {
    loading.value.refunds = false
  }
}

const fetchDisputes = async () => {
  loading.value.disputes = true
  
  try {
    const response = await csApi.getDisputes()
    if (response.data.success) {
      disputes.value = response.data.disputes
      stats.value.activeDisputes = disputes.value.filter(d => d.status === 'active').length
    }
  } catch (err: any) {
    console.error('Failed to fetch disputes:', err)
  } finally {
    loading.value.disputes = false
  }
}

const applyRefundFilters = () => {
  fetchRefunds()
}

const resetRefundFilters = () => {
  Object.assign(refundFilters, { status: '' })
  fetchRefunds()
}

const approveRefund = async (refundId: string) => {
  if (!confirm('Are you sure you want to approve this refund request?')) return
  
  processing.value.refund = true
  
  try {
    const response = await csApi.processRefund(refundId, {
      approved: true,
      reason: 'Refund approved by customer service'
    })
    
    if (response.data.success) {
      await fetchRefunds()
    }
  } catch (err: any) {
    console.error('Failed to approve refund:', err)
  } finally {
    processing.value.refund = false
  }
}

const rejectRefund = async (refundId: string) => {
  const reason = prompt('Please provide a reason for rejection:')
  if (!reason) return
  
  processing.value.refund = true
  
  try {
    const response = await csApi.processRefund(refundId, {
      approved: false,
      reason
    })
    
    if (response.data.success) {
      await fetchRefunds()
    }
  } catch (err: any) {
    console.error('Failed to reject refund:', err)
  } finally {
    processing.value.refund = false
  }
}

const openResolveDialog = (dispute: Dispute) => {
  resolveDialog.show = true
  resolveDialog.disputeId = dispute.id
  resolveDialog.resolution = ''
  resolveDialog.notes = ''
}

const closeResolveDialog = () => {
  resolveDialog.show = false
  resolveDialog.disputeId = ''
  resolveDialog.resolution = ''
  resolveDialog.notes = ''
}

const resolveDispute = async () => {
  if (!resolveDialog.disputeId) return
  
  processing.value.dispute = true
  
  try {
    const response = await csApi.resolveDispute(resolveDialog.disputeId, {
      resolution: resolveDialog.resolution,
      notes: resolveDialog.notes
    })
    
    if (response.data.success) {
      closeResolveDialog()
      await fetchDisputes()
    }
  } catch (err: any) {
    console.error('Failed to resolve dispute:', err)
  } finally {
    processing.value.dispute = false
  }
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  if (user.value?.role !== 'cs') {
    router.push('/')
    return
  }
  
  fetchRefunds()
  fetchDisputes()
})
</script>
