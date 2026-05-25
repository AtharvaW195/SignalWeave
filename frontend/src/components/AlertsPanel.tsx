import React from 'react'

export default function AlertsPanel({alerts, onSelect}:{alerts:any[], onSelect?: (item:any)=>void}){
  return (
    <div className="panel panel-stack">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Alert feed</p>
          <h3>Recent alerts</h3>
        </div>
      </div>
      <div className="card-list">
        {alerts.length===0 && <div className="empty-state">No alerts yet. Watch the tape for spikes, widening spreads, or volatility bursts.</div>}
        {alerts.map((a:any,idx:number)=> (
          <button key={idx} type="button" className="card-row" onClick={()=>onSelect?.(a)}>
            <div className="card-row-top">
              <strong>{a.symbol || a.detector}</strong>
              <span className={`severity severity-${String(a.severity || 'low').toLowerCase()}`}>{a.severity || 'LOW'}</span>
            </div>
            <div className="muted">{a.detector}</div>
            <div className="card-copy">{a.reason}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
