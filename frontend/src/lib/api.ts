import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (credentials: { email: string; password: string }) =>
    api.post('/auth/login', credentials),
  
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  
  getMe: () => api.get('/users/me'),
}

export const tasksApi = {
  getTasks: (params?: any) => api.get('/tasks', { params }),
  getTask: (id: string) => api.get(`/tasks/${id}`),
  createTask: (data: any) => api.post('/tasks', data),
  updateTask: (id: string, data: any) => api.put(`/tasks/${id}`, data),
  deleteTask: (id: string) => api.delete(`/tasks/${id}`),
}

export const bidsApi = {
  createBid: (taskId: string, data: CreateBidData) => 
    api.post(`/tasks/${taskId}/bids`, data),
  
  getTaskBids: (taskId: string) => 
    api.get(`/tasks/${taskId}/bids`),
  
  acceptBid: (taskId: string, bidId: string) => 
    api.post(`/tasks/${taskId}/bids/accept`, { bid_id: bidId }),
  
  rejectBid: (taskId: string, bidId: string) => 
    api.delete(`/tasks/${taskId}/bids/${bidId}`),
  
  getUserBids: (params?: any) => 
    api.get('/bids', { params }),
}

export const ordersApi = {
  getOrders: (params?: any) => 
    api.get('/orders', { params }),
  
  getOrder: (orderId: string) => 
    api.get(`/orders/${orderId}`),
  
  payOrder: (orderId: string) => 
    api.post(`/orders/${orderId}/pay`),
  
  deliverOrder: (orderId: string, data: any) => 
    api.post(`/orders/${orderId}/deliver`, data),
  
  acceptOrder: (orderId: string) => 
    api.post(`/orders/${orderId}/accept`),
  
  rejectOrder: (orderId: string, data: { reason: string }) => 
    api.post(`/orders/${orderId}/reject`, data),
  
  cancelOrder: (orderId: string) => 
    api.post(`/orders/${orderId}/cancel`),
}

// Messages API
export const messagesApi = {
  getMessages: (orderId: string) => 
    api.get(`/orders/${orderId}/messages`),
  
  sendMessage: (orderId: string, data: { content: string }) => 
    api.post(`/orders/${orderId}/messages`, data),
}

// Customer Service API
export const csApi = {
  getRefundRequests: (params?: any) => 
    api.get('/refund-requests', { params }),
  
  getRefundRequest: (refundId: string) => 
    api.get(`/refund-requests/${refundId}`),
  
  processRefund: (refundId: string, data: { approved: boolean; reason: string }) => 
    api.post(`/refund-requests/${refundId}/process`, data),
  
  getDisputes: () => 
    api.get('/disputes'),
  
  getDispute: (disputeId: string) => 
    api.get(`/disputes/${disputeId}`),
  
  resolveDispute: (disputeId: string, data: { resolution: string; notes: string }) => 
    api.post(`/disputes/${disputeId}/resolve`, data),
}

export default api
