import { useEffect, useRef, useCallback, useState } from 'react'

interface WebSocketMessage {
  type: 'progress' | 'complete' | 'error' | 'pong'
  job_id?: string
  progress?: number
  message?: string
  result?: any
  error?: string
  data?: any
}

type MessageHandler = (data: WebSocketMessage) => void

class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string = ''
  private handlers: Map<string, MessageHandler[]> = new Map()
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 3000

  connect(url: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.url = url
    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('open', { type: 'open' })
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage
          this.emit('message', data)
          
          if (data.type === 'progress') {
            this.emit('progress', data)
          } else if (data.type === 'complete') {
            this.emit('complete', data)
          } else if (data.type === 'error') {
            this.emit('error', data)
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.emit('close', { type: 'close' })
        this.handleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', { type: 'error', error: 'Connection error' })
      }
    } catch (e) {
      console.error('Failed to create WebSocket:', e)
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)
      setTimeout(() => {
        this.connect(this.url)
      }, this.reconnectDelay)
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.handlers.clear()
  }

  on(event: string, handler: MessageHandler): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, [])
    }
    this.handlers.get(event)?.push(handler)
  }

  off(event: string, handler: MessageHandler): void {
    const handlers = this.handlers.get(event)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  private emit(event: string, data: WebSocketMessage): void {
    const handlers = this.handlers.get(event)
    if (handlers) {
      handlers.forEach(handler => handler(data))
    }
  }

  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

const wsClient = new WebSocketClient()

export const useWebSocket = (jobId: string | null) => {
  const [progress, setProgress] = useState<number>(0)
  const [status, setStatus] = useState<string>('')
  const [currentStep, setCurrentStep] = useState<string>('')
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')
  const [isConnected, setIsConnected] = useState(false)

  const connect = useCallback(() => {
    if (!jobId) return

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws/jobs/${jobId}`
    wsClient.connect(wsUrl)
    
    wsClient.on('open', () => {
      setIsConnected(true)
    })

    wsClient.on('progress', (data) => {
      setProgress(data.progress || 0)
      setCurrentStep(data.message || '')
    })

    wsClient.on('complete', (data) => {
      setProgress(100)
      setStatus('completed')
      setResult(data.result)
    })

    wsClient.on('error', (data) => {
      setError(data.error || 'Unknown error')
      setStatus('failed')
    })

    wsClient.on('close', () => {
      setIsConnected(false)
    })
  }, [jobId])

  const disconnect = useCallback(() => {
    wsClient.disconnect()
    setIsConnected(false)
    setProgress(0)
    setStatus('')
    setCurrentStep('')
    setResult(null)
    setError('')
  }, [])

  useEffect(() => {
    if (jobId) {
      connect()
    }
    return () => {
      disconnect()
    }
  }, [jobId, connect, disconnect])

  return {
    progress,
    status,
    currentStep,
    result,
    error,
    isConnected,
    connect,
    disconnect
  }
}

export const getWebSocketClient = () => wsClient

export default wsClient
