import { useEffect, useState } from 'react'
import { AlertPanel } from '../components/AlertPanel'
import { EventTable } from '../components/EventTable'
import { MetricCard } from '../components/MetricCard'
import { ModeSelector } from '../components/ModeSelector'
import { TrendChart } from '../components/TrendChart'
import { getHealth, getModes } from '../services/api'
import { connectStream } from '../services/ws'
import type { AggregatedDecision, ModeSummary, SourceType, StreamMetrics } from '../types'

const DEFAULT_MODE: SourceType = 'fintech'

function severityRank(severity: AggregatedDecision['severity'] | 'all'): number {
  if (severity === 'critical') return 4
  if (severity === 'high') return 3
  if (severity === 'medium') return 2
  if (severity === 'low') return 1
  return 0
}

export function Dashboard() {
  const [modes, setModes] = useState<ModeSummary[]>([])
  const [mode, setMode] = useState<SourceType>(DEFAULT_MODE)
  const [events, setEvents] = useState<AggregatedDecision[]>([])
  const [search, setSearch] = useState('')
  const [minimumSeverity, setMinimumSeverity] = useState<'all' | AggregatedDecision['severity']>('all')
  const [connectionState, setConnectionState] = useState<'connecting' | 'open' | 'closed' | 'error'>('connecting')
  const [metrics, setMetrics] = useState<StreamMetrics[]>([])

  useEffect(() => {
    let mounted = true
    void Promise.all([getModes(), getHealth()]).then(([availableModes, health]) => {
      if (!mounted) {
        return
      }
      setModes(availableModes)
      setMetrics(health.modes)
    })
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    const socket = connectStream(mode, {
      onMessage: message => {
        if (typeof message === 'object' && message !== null && 'type' in message) {
          const payload = message as { type: string; events?: AggregatedDecision[]; payload?: AggregatedDecision }
          if (payload.type === 'history' && payload.events) {
            setEvents(payload.events)
          }
          if (payload.type === 'tick' && payload.payload) {
            setEvents(previous => [payload.payload as AggregatedDecision, ...previous].slice(0, 60))
          }
        }
      },
      onStatus: status => setConnectionState(status),
    })

    return () => socket.close()
  }, [mode])

  useEffect(() => {
    const timer = window.setInterval(() => {
      void getHealth().then(health => setMetrics(health.modes))
    }, 5000)
    return () => window.clearInterval(timer)
  }, [])

  const filteredEvents = events.filter(event => {
    const text = `${event.symbol} ${event.reason} ${event.model}`.toLowerCase()
    const matchesSearch = text.includes(search.toLowerCase())
    const meetsSeverity = minimumSeverity === 'all' || severityRank(event.severity) >= severityRank(minimumSeverity)
    return matchesSearch && meetsSeverity
  })

  const alerts = filteredEvents.filter(event => event.is_anomaly)
  const selectedMetrics = metrics.find(item => item.mode === mode)
  const modeOptions: SourceType[] = modes.length > 0 ? modes.map(item => item.mode) : [DEFAULT_MODE, 'networking', 'system']
  const chartData = filteredEvents.slice(0, 12).reverse().map((event, index) => ({
    label: `${index}`,
    score: event.anomaly_score,
    latency: Number(event.tick.metadata['latency_ms'] ?? 0) / 100,
  }))

  return (
    <main className="dashboard-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Real-time event intelligence platform</p>
          <h1>SignalWeave</h1>
          <p className="hero-copy">
            Streaming tick surveillance for fintech, networking, and infrastructure telemetry with ML-assisted anomaly scoring.
          </p>
        </div>
        <div className={`connection-badge state-${connectionState}`}>
          <span>Connection</span>
          <strong>{connectionState}</strong>
        </div>
      </section>

      <section className="toolbar panel">
        <div>
          <span className="section-label">Mode</span>
          <ModeSelector
            value={mode}
            options={modeOptions}
            onChange={setMode}
          />
        </div>
        <div className="filters">
          <input
            type="search"
            value={search}
            onChange={event => setSearch(event.target.value)}
            placeholder="Search symbol, model, or reason"
          />
          <select value={minimumSeverity} onChange={event => setMinimumSeverity(event.target.value as any)}>
            <option value="all">All severities</option>
            <option value="low">Low+</option>
            <option value="medium">Medium+</option>
            <option value="high">High+</option>
            <option value="critical">Critical only</option>
          </select>
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard
          label="Throughput"
          value={`${selectedMetrics?.throughput_per_second ?? 0}`}
          detail="events / second"
          tone="cyan"
        />
        <MetricCard
          label="Latency"
          value={`${selectedMetrics?.average_latency_ms ?? 0} ms`}
          detail="decision pipeline latency"
          tone="amber"
        />
        <MetricCard
          label="Anomaly Rate"
          value={`${((selectedMetrics?.anomaly_rate ?? 0) * 100).toFixed(1)}%`}
          detail="detected anomalies"
          tone="rose"
        />
        <MetricCard
          label="Subscribers"
          value={`${selectedMetrics?.active_subscribers ?? 0}`}
          detail="live websocket clients"
          tone="emerald"
        />
      </section>

      <section className="content-grid">
        <TrendChart data={chartData} />
        <AlertPanel alerts={alerts} />
      </section>

      <section className="content-grid single-column">
        <EventTable events={filteredEvents} />
      </section>
    </main>
  )
}
