export type SourceType = 'fintech' | 'networking' | 'system'

export type TickType = 'price' | 'packet' | 'metric'

export interface TickEvent {
  event_id: string
  timestamp: number
  source: SourceType
  symbol: string
  tick_type: TickType
  value: number
  volume: number
  metadata: Record<string, unknown>
}

export interface FeatureSnapshot {
  rolling_mean: number
  rolling_std: number
  z_score: number
  ema: number
  volatility: number
  delta: number
  rate_of_change: number
  spike_intensity: number
  anomaly_history: number
  history_depth: number
}

export interface DetectorResult {
  layer: 'rule' | 'statistical' | 'ml'
  score: number
  is_anomaly: boolean
  reason: string
}

export interface AggregatedDecision {
  event_id: string
  source: SourceType
  symbol: string
  anomaly_score: number
  confidence: number
  severity: 'low' | 'medium' | 'high' | 'critical'
  is_anomaly: boolean
  reason: string
  model: string
  features: FeatureSnapshot
  tick: TickEvent
  detector_breakdown: Record<string, DetectorResult>
}

export interface StreamMetrics {
  mode: SourceType
  throughput_per_second: number
  average_latency_ms: number
  anomaly_rate: number
  total_events: number
  active_subscribers: number
}

export interface ModeSummary {
  mode: SourceType
  description: string
}

export interface HealthPayload {
  status: string
  modes: StreamMetrics[]
}
