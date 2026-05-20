import type { HealthPayload, ModeSummary } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function getModes(): Promise<ModeSummary[]> {
  return requestJson<ModeSummary[]>('/api/modes')
}

export function getHealth(): Promise<HealthPayload> {
  return requestJson<HealthPayload>('/api/health')
}

export function getHistory(mode: string) {
  return requestJson<{ mode: string; events: unknown[] }>(`/api/history/${mode}`)
}
