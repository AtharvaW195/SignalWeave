import React, {useMemo, useState} from 'react'
import LiveFeed, { MarketAnomaly } from './components/LiveFeed'
import DBView from './components/DBView'
import PriceChart from './components/PriceChart'
import AlertsPanel from './components/AlertsPanel'
import AnomalyTable from './components/AnomalyTable'
import TradesPanel from './components/TradesPanel'
import ErrorBoundary from './components/ErrorBoundary'
import type { PricePoint } from './components/PriceChart'

function formatImpact(anomaly?: MarketAnomaly | null) {
  if (!anomaly) {
    return 'Click an anomaly to see what it means for the market.'
  }
  const detector = anomaly.detector
  if (detector === 'rule:price_spike') {
    return 'A sudden price spike can mean news, algorithmic momentum, or a repricing event. If sustained, traders may treat it as trend continuation; if it reverses, it may be a stop-run or exhaustion move.'
  }
  if (detector === 'rule:volume_jump') {
    return 'A volume jump often means institutional participation or a reaction to a catalyst. It can confirm a move or signal heightened interest before a breakout.'
  }
  if (detector === 'rule:spread_widen') {
    return 'A widening spread usually means liquidity is thinning. Market makers may be stepping back, execution cost rises, and the symbol becomes harder to trade efficiently.'
  }
  if (detector === 'stat:zscore') {
    return 'A large z-score means the price is far from its recent average. That can indicate overextension, mean-reversion risk, or a true regime change.'
  }
  if (detector === 'stat:volatility') {
    return 'A volatility spike means price swings are accelerating. That usually raises risk, makes short-term signals noisier, and can precede a larger repricing.'
  }
  if (detector === 'ml:ensemble') {
    return 'The ML model sees a combination of unusual price, volume, and spread behavior. This is the kind of anomaly that can catch multi-factor market stress before simple rules do.'
  }
  return anomaly.marketMeaning || 'This event suggests the symbol is trading outside its recent normal behavior.'
}

export default function App() {
  const [selectedAnomaly, setSelectedAnomaly] = useState<MarketAnomaly | null>(null)
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL')
  const [chartMode, setChartMode] = useState<'line' | 'candle'>('line')
  const [timeWindow, setTimeWindow] = useState<'1m' | '5m' | '15m' | '1h' | 'all'>('5m')
  const [priceSeries, setPriceSeries] = useState<Record<string, PricePoint[]>>({})
  const [latestAlerts, setLatestAlerts] = useState<MarketAnomaly[]>([])
  const [trades, setTrades] = useState<any[]>([])

  const activeSeries = priceSeries[selectedSymbol] || []

  const summaryCards = useMemo(() => {
    const latestPrice = activeSeries[activeSeries.length - 1]
    const change = activeSeries.length > 1 ? latestPrice.price - activeSeries[0].price : 0
    const changePct = activeSeries.length > 1 && activeSeries[0].price ? (change / activeSeries[0].price) * 100 : 0
    return [
      { label: 'Active Symbol', value: selectedSymbol, detail: 'Focused market stream' },
      { label: 'Latest Price', value: latestPrice ? latestPrice.price.toFixed(2) : '--', detail: 'Streaming from simulator' },
      { label: 'Session Change', value: `${change >= 0 ? '+' : ''}${change.toFixed(2)}`, detail: `${changePct >= 0 ? '+' : ''}${changePct.toFixed(2)}%` },
      { label: 'Alerts', value: `${latestAlerts.length}`, detail: 'Recent anomaly hits' },
    ]
  }, [activeSeries, latestAlerts.length, selectedSymbol])

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">SignalWeave</p>
          <h1>Real-time market surveillance for US equities</h1>
          <p className="hero-copy">
            Live streaming tick data, anomaly detection, and market context in one dashboard. Click any anomaly to see what it means for liquidity, volatility, and market behavior.
          </p>
        </div>
        <div className="hero-badge">
          <span>Demo mode</span>
          <strong>Simulated market tape</strong>
        </div>
      </header>

      <div className="summary-grid">
        {summaryCards.map((card) => (
          <div key={card.label} className="summary-card">
            <div className="muted">{card.label}</div>
            <div className="summary-value">{card.value}</div>
            <div className="muted">{card.detail}</div>
          </div>
        ))}
      </div>

      <main className="dashboard-layout">
        <div className="dashboard-main">
          <section className="panel panel-large">
            <div className="panel-header panel-header-tight">
              <div>
                <p className="eyebrow">Coverage</p>
                <h3>Focus symbol</h3>
              </div>
              <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)}>
                {['AAPL', 'TSLA', 'NVDA', 'MSFT', 'SPY'].map((symbol) => (
                  <option key={symbol}>{symbol}</option>
                ))}
              </select>
            </div>
            <ErrorBoundary fallback={<div className="chart-empty">The chart could not load right now. The rest of the dashboard is still available.</div>}>
              <PriceChart
                points={activeSeries}
                symbol={selectedSymbol}
                timeWindow={timeWindow}
                chartMode={chartMode}
                onTimeWindowChange={setTimeWindow}
                onModeChange={setChartMode}
              />
            </ErrorBoundary>
          </section>

          <LiveFeed
            onStreamTick={(tick) => {
              const symbol = tick?.symbol || 'AAPL'
              const point: PricePoint = {
                timestamp: Number(tick?.timestamp || Date.now() / 1000),
                price: Number(tick?.price || 0),
                volume: Number(tick?.volume || 0),
              }
              setPriceSeries((prev) => ({
                ...prev,
                [symbol]: (prev[symbol] || []).concat([point]).slice(-300),
              }))
              if (!priceSeries[selectedSymbol] && symbol === selectedSymbol) {
                setSelectedSymbol(symbol)
              }
            }}
            onAnomalyDetected={(anomaly) => {
              setLatestAlerts((prev) => [anomaly].concat(prev).slice(0, 80))
              setTrades((prev) => {
                if (anomaly.severity === 'HIGH') {
                  return [
                    {
                      action: anomaly.detector.includes('price') ? 'BUY' : 'HOLD',
                      symbol: anomaly.symbol,
                      size: anomaly.severity === 'HIGH' ? 100 : 25,
                      price: anomaly.price,
                      reason: anomaly.marketMeaning,
                    },
                  ].concat(prev).slice(0, 20)
                }
                return prev
              })
              setSelectedAnomaly(anomaly)
            }}
          />
        </div>

        <aside className="dashboard-side">
          <section className="panel detail-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Selected anomaly</p>
                <h3>What it means</h3>
              </div>
            </div>
            {selectedAnomaly ? (
              <div className="detail-stack">
                <div className="detail-head">
                  <div>
                    <strong>{selectedAnomaly.symbol}</strong>
                    <div className="muted">{selectedAnomaly.detector}</div>
                  </div>
                  <span className={`severity severity-${selectedAnomaly.severity.toLowerCase()}`}>{selectedAnomaly.severity}</span>
                </div>
                <div className="detail-metric">
                  <span className="muted">Reason</span>
                  <strong>{selectedAnomaly.reason}</strong>
                </div>
                <div className="detail-metric">
                  <span className="muted">Price / Volume</span>
                  <strong>{selectedAnomaly.price.toFixed(2)} / {selectedAnomaly.volume}</strong>
                </div>
                {selectedAnomaly.zScore !== undefined && (
                  <div className="detail-metric">
                    <span className="muted">Z-score</span>
                    <strong>{selectedAnomaly.zScore.toFixed(2)}</strong>
                  </div>
                )}
                <div className="market-explanation">{formatImpact(selectedAnomaly)}</div>
              </div>
            ) : (
              <div className="muted">Click an anomaly in the timeline to see a market explanation here.</div>
            )}
          </section>

          <AlertsPanel alerts={latestAlerts} onSelect={setSelectedAnomaly} />
          <AnomalyTable rows={latestAlerts} onSelect={setSelectedAnomaly} selectedId={selectedAnomaly?.id} />
          <TradesPanel trades={trades} />
        </aside>
      </main>

      <section className="bottom-grid">
        <DBView />
      </section>
    </div>
  )
}
