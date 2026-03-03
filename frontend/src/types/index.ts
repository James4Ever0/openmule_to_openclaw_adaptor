export interface User {
  id: string
  username: string
  email?: string
  role: 'client' | 'ai' | 'cs'
  balance?: string
  created_at: string
}

export interface Task {
  id: string
  title: string
  description: string
  budget: string
  deadline: string
  status: 'open' | 'assigned' | 'completed' | 'cancelled'
  client_id: string
  category: string
  attachments?: string[]
  created_at: string
  updated_at: string
  client?: {
    id: string
    username: string
  }
  bid_count?: number
  bids?: Bid[]
}

export interface Bid {
  id: string
  task_id: string
  ai_id: string
  ai_username: string
  amount: string
  estimated_days: number
  message: string
  status: 'pending' | 'accepted' | 'rejected'
  created_at: string
}

export interface Order {
  id: string
  task_id: string
  task: {
    id: string
    title: string
    description: string
  }
  client: {
    id: string
    username: string
  }
  ai: {
    id: string
    username: string
  }
  amount: string
  status: 'pending_payment' | 'assigned' | 'delivered' | 'completed' | 'disputed' | 'refunded' | 'cancelled'
  deadline: string
  payment_status: 'unpaid' | 'paid' | 'refunded'
  paid_at?: string
  delivered_at?: string
  completed_at?: string
  deliverables?: Deliverable[]
  created_at: string
  updated_at: string
}

export interface Deliverable {
  id: string
  file_url: string
  description: string
  created_at: string
}

export interface Message {
  id: string
  sender_id: string
  sender_type: 'client' | 'ai'
  content: string
  file_url?: string
  created_at: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface CreateTaskData {
  title: string
  description: string
  budget: string
  deadline: string
  category: string
  attachments?: string[]
}

export interface CreateBidData {
  amount: string
  estimated_days: number
  message: string
}

export interface TaskFilters {
  status?: string
  category?: string
  min_budget?: string
  max_budget?: string
  sort?: 'new' | 'budget_desc' | 'budget_asc'
  page?: number
  limit?: number
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: {
    code: number
    message: string
  }
  message?: string
}
