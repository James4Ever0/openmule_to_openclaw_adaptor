import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Type definitions
interface CreateBidData {
  amount: string
  estimated_days: number
  message: string
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    // console.log("LocalStorage token:", localStorage.getItem('token'))
    // console.log('AuthStore token:', authStore.token)
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

// File Upload API
export const uploadsApi = {
  uploadFile: (file: File, comment?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (comment) {
      formData.append('comment', comment)
    }
    
    return api.post('/uploads/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  
  getUserFiles: () => 
    api.get('/uploads'),
  
  getFileInfo: (fileId: string) => 
    api.get(`/uploads/${fileId}`),
  
  downloadFile: (fileId: string) => {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000'
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const downloadUrl=`${baseUrl}/uploads/${fileId}/download`
    console.log("baseUrl", baseUrl)
    console.log("fileId", fileId)
    console.log('Downloading file from:', downloadUrl)

    return fetch(downloadUrl, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
    }).then(response => {
      if (!response.ok) {
        throw new Error('Download failed')
      }
      return response.blob()
    })
  },
  
  updateFileComment: (fileId: string, comment: string) => 
    api.put(`/uploads/${fileId}`, { comment }),
  
  deleteFile: (fileId: string) => 
    api.delete(`/uploads/${fileId}`),
}

// Task Files API
export const taskFilesApi = {
  addFileToTask: (taskId: string, fileId: string) =>
    api.post('/task-files/', { task_id: taskId, file_id: fileId }),
  
  getTaskFiles: (taskId: string) =>
    api.get(`/task-files/task/${taskId}`),
  
  getFileTasks: (fileId: string) =>
    api.get(`/task-files/file/${fileId}/tasks`),
  
  removeFileFromTask: (taskFileId: string) =>
    api.delete(`/task-files/${taskFileId}`),
  
  removeFileFromTaskByIds: (taskId: string, fileId: string) =>
    api.delete(`/task-files/task/${taskId}/file/${fileId}`),
}

export default api
