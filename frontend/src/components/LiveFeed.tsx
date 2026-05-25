import React, {useEffect, useMemo, useState} from 'react'

export type MarketAnomaly = {
  id: string
  detector: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH'
  reason: string
  symbol: string
  price: number
  volume: number
  timestamp: number
  zScore?: number
  impact: string
  marketMeaning: string
}

function buildMarketMeaning(detector: string, severity: string, reason: string, price: number, volume: number) {
  const base = `${detector} flagged a ${severity.toLowerCase()} risk.`
  if (detector.startsWith('rule:price_spike')) {
    return `${base} Fast price movement can indicate news, momentum trading, or a sharp repricing in ${reason ? reason.toLowerCase() : 'the symbol'}.`
  }
  if (detector.startsWith('rule:volume_jump')) {
    return `${base} Volume surged, which often means institutional activity, earnings reaction, or unusual market attention.`
  }
  if (detector.startsWith('rule:spread_widen')) {
    return `${base} The bid/ask spread widened, which usually means lower liquidity, higher uncertainty, or temporarily stressed market conditions.`
  }
  if (detector.startsWith('stat:zscore')) {
    return `${base} The current price is far from its recent average, which suggests a potential break from the symbol's normal trading range.`
  }
  if (detector.startsWith('stat:volatility')) {
    return `${base} Price movement is moving faster than the recent volatility baseline, which can signal an unstable microstructure or abrupt repricing.`
  }
  if (detector.startsWith('ml:ensemble')) {
    return `${base} The ML model sees the full pattern as unusual. That matters because the anomaly may come from a combination of price, volume, and spread behavior.`
  }
  return `${base} This usually means the market behavior is outside its recent pattern and deserves review.`
}

export default function LiveFeed({
  onPriceSeries,
  onAnomalyDetected,
  onStreamTick,
}: {
  onPriceSeries?: (symbol: string, prices: number[]) => void
  onAnomalyDetected?: (anomaly: MarketAnomaly) => void
  onStreamTick?: (tick: any, payload: any) => void
}) {
  const [messages, setMessages] = useState<any[]>([])
  const [alerts, setAlerts] = useState<MarketAnomaly[]>([])
  const [activeSymbol, setActiveSymbol] = useState<string>('AAPL')
  const [series, setSeries] = useState<Record<string, number[]>>({})

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/ticks')
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        const tick = data.tick || {}
        const symbol = tick.symbol || 'AAPL'
        const price = Number(tick.price || 0)
        const volume = Number(tick.volume || 0)

        setMessages((m) => [data].concat(m).slice(0, 60))

        setSeries((prev) => {
          const next = { ...prev }
          next[symbol] = (next[symbol] || []).concat([price]).slice(-100)
          onPriceSeries?.(symbol, next[symbol])
          return next
        })

        onStreamTick?.(tick, data)

        const derived: MarketAnomaly[] = []
        if (data.rules) {
          Object.keys(data.rules).forEach((key) => {
            const item = data.rules[key]
            if (item?.is_anomaly) {
              const detector = `rule:${key}`
              derived.push({
                id: `${detector}-${Date.now()}-${Math.random()}`,
                detector,
                severity: 'HIGH',
                reason: item.reason || 'Rule-based anomaly',
                symbol,
                price,
                volume,
                timestamp: tick.timestamp || Date.now(),
                impact: key === 'price_spike'
                  ? 'Possible momentum burst or repricing'
                  : key === 'volume_jump'
                    ? 'Volume shock; market participation changed suddenly'
                    : 'Liquidity stress is likely increasing',
                marketMeaning: buildMarketMeaning(detector, 'HIGH', item.reason || '', price, volume),
              })
            }
          })
        }

        if (data.stat?.zscore?.is_anomaly) {
          const detector = 'stat:zscore'
          derived.push({
            id: `${detector}-${Date.now()}-${Math.random()}`,
            detector,
            severity: 'MEDIUM',
            reason: data.stat?.zscore?.reason || 'Z-score deviation',
            symbol,
            price,
            volume,
            timestamp: tick.timestamp || Date.now(),
            zScore: data.stat?.zscore?.z_score,
            impact: 'Price is stretched relative to recent history',
            marketMeaning: buildMarketMeaning(detector, 'MEDIUM', data.stat?.zscore?.reason || '', price, volume),
          })
        }

        if (data.stat?.volatility?.is_anomaly) {
          const detector = 'stat:volatility'
          derived.push({
            id: `${detector}-${Date.now()}-${Math.random()}`,
            detector,
            severity: 'MEDIUM',
            reason: data.stat?.volatility?.reason || 'Volatility spike',
            symbol,
            price,
            volume,
            timestamp: tick.timestamp || Date.now(),
            impact: 'Short-term volatility has expanded',
            marketMeaning: buildMarketMeaning(detector, 'MEDIUM', data.stat?.volatility?.reason || '', price, volume),
          })
        }

        if (data.ml?.anomaly_score >= 0.7) {
          const detector = 'ml:ensemble'
          derived.push({
            id: `${detector}-${Date.now()}-${Math.random()}`,
            detector,
            severity: 'HIGH',
            reason: `ML anomaly score ${Number(data.ml.anomaly_score).toFixed(2)}`,
            symbol,
            price,
            volume,
            timestamp: tick.timestamp || Date.now(),
            impact: 'Multiple market features look unusual together',
            marketMeaning: buildMarketMeaning(detector, 'HIGH', '', price, volume),
          })
        }

        if (derived.length) {
          setAlerts((prev) => derived.concat(prev).slice(0, 80))
          derived.forEach((item) => onAnomalyDetected?.(item))
        }
      } catch (e) {
        console.error(e)
      }
    }
    ws.onclose = () => console.log('ws closed')
    return () => ws.close()
  }, [onAnomalyDetected, onPriceSeries, onStreamTick])

  const liveMessages = useMemo(() => messages.slice(0, 30), [messages])

  return (
    <div className="dashboard-grid">
      <section className="panel panel-large">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Live market tape</p>
            <h3>Real-time tick feed</h3>
          </div>
          <select value={activeSymbol} onChange={(e) => setActiveSymbol(e.target.value)}>
            {Object.keys(series).length === 0 ? (
              <>
                <option>AAPL</option>
                <option>TSLA</option>
                <option>NVDA</option>
                <option>MSFT</option>
                <option>SPY</option>
              </>
            ) : (
              Object.keys(series).map((symbol) => <option key={symbol}>{symbol}</option>)
            )}
          </select>
        </div>
        <div className="tick-stream">
          {liveMessages.map((m, idx) => (
            <div key={idx} className="tick-row">
              <div>
                <strong>{m.tick.symbol}</strong>
                <span>{Number(m.tick.price).toFixed(2)}</span>
              </div>
              <div className="muted">vol {m.tick.volume} • spread {Number(m.tick.bid_ask_spread || 0).toFixed(4)}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="panel panel-side">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Market stress</p>
            <h3>Anomaly timeline</h3>
          </div>
        </div>
        <div className="alert-list">
          {alerts.slice(0, 12).map((alert) => (
            <button
              key={alert.id}
              className="alert-card"
              type="button"
              onClick={() => onAnomalyDetected?.(alert)}
            >
              <div className="alert-card-top">
                <strong>{alert.symbol}</strong>
                <span className={`severity severity-${alert.severity.toLowerCase()}`}>{alert.severity}</span>
              </div>
              <div className="alert-title">{alert.detector.replace('rule:', '').replace('stat:', '').replace('ml:', 'ML • ')}</div>
              <div className="muted">{alert.reason}</div>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
