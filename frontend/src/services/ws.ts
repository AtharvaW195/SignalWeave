import type { SourceType } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function wsBaseUrl(): string {
  const url = new URL(API_BASE)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return url.toString().replace(/\/$/, '')
}

export function connectStream(
  mode: SourceType,
  handlers: {
    onMessage: (message: unknown) => void
    onStatus: (status: 'connecting' | 'open' | 'closed' | 'error') => void
  },
): WebSocket {
  const socket = new WebSocket(`${wsBaseUrl()}/ws/stream/${mode}`)
  handlers.onStatus('connecting')
  socket.onopen = () => handlers.onStatus('open')
  socket.onclose = () => handlers.onStatus('closed')
  socket.onerror = () => handlers.onStatus('error')
  socket.onmessage = event => {
    try {
      handlers.onMessage(JSON.parse(event.data))
    } catch {
      handlers.onMessage(event.data)
    }
  }
  return socket
}
