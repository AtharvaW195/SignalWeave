import React from 'react'

export default function TradesPanel({trades}:{trades:any[]}){
  return (
    <div className="panel panel-stack">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Response engine</p>
          <h3>Simulated trades</h3>
        </div>
      </div>
      <div className="card-list scroll-list">
        {trades.length===0 && <div className="empty-state">No simulated trades yet.</div>}
        {trades.map((t:any,idx:number)=> (
          <div key={idx} className="trade-row">
            <div className="card-row-top">
              <strong>{t.action}</strong>
              <span>{t.symbol}</span>
            </div>
            <div className="muted">{t.size} shares @ {t.price}</div>
            <div className="card-copy">{t.reason}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
