import type { AggregatedDecision } from '../types'

interface EventTableProps {
  events: AggregatedDecision[]
}

function formatTimestamp(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleTimeString([], { hour12: false })
}

export function EventTable({ events }: EventTableProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Live Event Stream</h2>
        <p>Unified tick events with feature snapshots and decision output.</p>
      </div>
      <div className="event-table">
        {events.map(event => (
          <div className="event-row" key={event.event_id}>
            <div>
              <strong>{event.symbol}</strong>
              <span>{formatTimestamp(event.tick.timestamp)} · {event.source}</span>
            </div>
            <div className="event-row-metrics">
              <span className={`severity-pill severity-${event.severity}`}>{event.severity}</span>
              <span>{event.anomaly_score.toFixed(2)}</span>
              <span>{event.reason}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
