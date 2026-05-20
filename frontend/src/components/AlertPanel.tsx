import type { AggregatedDecision } from '../types'

interface AlertPanelProps {
  alerts: AggregatedDecision[]
}

export function AlertPanel({ alerts }: AlertPanelProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Anomaly Alerts</h2>
        <p>ML and statistical detections promoted into the final decision layer.</p>
      </div>
      <div className="alert-list">
        {alerts.slice(0, 6).map(alert => (
          <article key={alert.event_id} className="alert-card">
            <div className="alert-title-row">
              <strong>{alert.symbol}</strong>
              <span>{alert.model}</span>
            </div>
            <p>{alert.reason}</p>
            <div className="alert-meta">
              <span>{alert.source}</span>
              <span>{alert.confidence.toFixed(2)} confidence</span>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
