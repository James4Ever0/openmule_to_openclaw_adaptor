import { ref, onUnmounted } from 'vue'

export interface WebSocketMessage {
  type: 'message' | 'order_update' | 'bid_update'
  id?: string
  order_id?: string
  sender_id?: string
  content?: string
  timestamp?: string
  data?: any
}

export class WebSocketManager {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectTimeout: number | null = null
  private messageHandlers: Map<string, ((message: WebSocketMessage) => void)> = new Map()
  private connectionStatus = ref<'connecting' | 'connected' | 'disconnected'>('disconnected')

  constructor(private url: string) {}

  connect(orderId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.url}?order_id=${orderId}`)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.connectionStatus.value = 'connected'
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.connectionStatus.value = 'disconnected'
          this.attemptReconnect(orderId)
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.connectionStatus.value = 'disconnected'
          reject(error)
        }

        this.connectionStatus.value = 'connecting'
      } catch (error) {
        reject(error)
      }
    })
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
    }
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.connectionStatus.value = 'disconnected'
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected, cannot send message')
    }
  }

  onMessage(type: string, handler: (message: WebSocketMessage) => void) {
    this.messageHandlers.set(type, handler)
  }

  offMessage(type: string) {
    this.messageHandlers.delete(type)
  }

  isConnected() {
    return this.connectionStatus.value === 'connected'
  }

  getStatus() {
    return this.connectionStatus
  }

  private handleMessage(message: WebSocketMessage) {
    const handler = this.messageHandlers.get(message.type)
    if (handler) {
      handler(message)
    }
  }

  private attemptReconnect(orderId: string) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    this.reconnectTimeout = window.setTimeout(() => {
      this.connect(orderId).catch(error => {
        console.error('Reconnection failed:', error)
      })
    }, delay)
  }
}

// Singleton instance for managing WebSocket connections
export const wsManager = new WebSocketManager(
  import.meta.env.VITE_WS_URL || 'ws://localhost:3000/api/v1/orders'
)

// Composable for using WebSocket in Vue components
export function useWebSocket(orderId: string) {
  const isConnected = ref(false)
  const messages = ref<WebSocketMessage[]>([])

  const connect = () => {
    return wsManager.connect(orderId)
  }

  const disconnect = () => {
    wsManager.disconnect()
  }

  const send = (message: any) => {
    wsManager.send(message)
  }

  const onMessage = (type: string, handler: (message: WebSocketMessage) => void) => {
    wsManager.onMessage(type, handler)
  }

  const offMessage = (type: string) => {
    wsManager.offMessage(type)
  }

  // Set up message handlers
  wsManager.onMessage('message', (message) => {
    if (message.type === 'message') {
      messages.value.push(message)
    }
  })

  // Watch connection status
  const statusWatcher = wsManager.getStatus()
  isConnected.value = statusWatcher.value === 'connected'

  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    disconnect,
    send,
    onMessage,
    offMessage,
    isConnected,
    messages,
    status: statusWatcher
  }
}
