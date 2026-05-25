import React, {useState} from 'react'

export default function DBView(){
  const [ticks, setTicks] = useState<any[]>([])
  const [anoms, setAnoms] = useState<any[]>([])

  async function loadTicks(){
    const r = await fetch('/api/recent_ticks')
    const j = await r.json()
    setTicks(j)
  }

  async function loadAnoms(){
    const r = await fetch('/api/recent_anomalies')
    const j = await r.json()
    setAnoms(j)
  }

  return (
    <div style={{marginTop:16}}>
      <h3>Database (demo)</h3>
      <div style={{display:'flex', gap:8}}>
        <button onClick={loadTicks}>Load recent ticks</button>
        <a href="/api/export/ticks.csv" target="_blank" rel="noreferrer"><button>Download ticks CSV</button></a>
        <button onClick={loadAnoms}>Load recent anomalies</button>
        <a href="/api/export/anomalies.csv" target="_blank" rel="noreferrer"><button>Download anomalies CSV</button></a>
      </div>

      <div style={{display:'flex', gap:16, marginTop:12}}>
        <div style={{flex:1}}>
          <h4>Ticks</h4>
          <div style={{maxHeight:250, overflow:'auto', background:'#fff', padding:8}}>
            {ticks.map((t:any)=> (
              <div key={t.id} style={{borderBottom:'1px solid #eee', padding:6}}>
                <div><strong>{t.symbol}</strong> {t.price} vol:{t.volume}</div>
                <div style={{fontSize:12,color:'#666'}}>{new Date(t.ts_epoch*1000).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
        <div style={{flex:1}}>
          <h4>Anomalies</h4>
          <div style={{maxHeight:250, overflow:'auto', background:'#fff', padding:8}}>
            {anoms.map((a:any)=> (
              <div key={a.id} style={{borderBottom:'1px solid #eee', padding:6}}>
                <div><strong>{a.detector}</strong> {a.severity} {a.reason}</div>
                <div style={{fontSize:12,color:'#666'}}>{new Date(a.detected_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
