import React from 'react'

export default function AnomalyTable({rows, onSelect, selectedId}:{rows:any[], onSelect?: (row:any)=>void, selectedId?: string | null}){
  return (
    <div className="panel panel-stack">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Audit trail</p>
          <h3>Anomaly history</h3>
        </div>
      </div>
      <div className="card-list scroll-list">
        {rows.length===0 && <div className="empty-state">No anomaly history yet.</div>}
        {rows.map((r:any)=> (
          <button
            key={r.id}
            type="button"
            className={`card-row ${selectedId === r.id ? 'card-row-selected' : ''}`}
            onClick={()=>onSelect?.(r)}
          >
            <div className="card-row-top">
              <strong>{r.symbol || r.detector}</strong>
              <span className={`severity severity-${String(r.severity || 'low').toLowerCase()}`}>{r.severity || 'LOW'}</span>
            </div>
            <div className="muted">{r.detector}</div>
            <div className="card-copy">{r.reason}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
