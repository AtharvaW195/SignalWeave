import React, {useMemo} from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

export type PricePoint = {
  timestamp: number
  price: number
  volume?: number
}

type ChartMode = 'line' | 'candle'
type TimeWindow = '1m' | '5m' | '15m' | '1h' | 'all'

type CandleBar = {
  start: number
  end: number
  open: number
  high: number
  low: number
  close: number
}

const WINDOW_SECONDS: Record<Exclude<TimeWindow, 'all'>, number> = {
  '1m': 60,
  '5m': 300,
  '15m': 900,
  '1h': 3600,
}

const WINDOW_LABELS: Record<TimeWindow, string> = {
  '1m': '1 min',
  '5m': '5 min',
  '15m': '15 min',
  '1h': '1 hr',
  'all': 'All',
}

function formatClock(ts: number) {
  return new Intl.DateTimeFormat('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(new Date(ts * 1000))
}

function filterByWindow(points: PricePoint[] = [], window: TimeWindow) {
  if (window === 'all' || points.length === 0) return points
  const cutoff = points[points.length - 1].timestamp - WINDOW_SECONDS[window]
  return points.filter((point) => point.timestamp >= cutoff)
}

function groupIntoCandles(points: PricePoint[], targetBars = 18): CandleBar[] {
  if (points.length === 0) return []
  const bucketSize = Math.max(1, Math.ceil(points.length / targetBars))
  const candles: CandleBar[] = []
  for (let i = 0; i < points.length; i += bucketSize) {
    const chunk = points.slice(i, i + bucketSize)
    if (!chunk.length) continue
    candles.push({
      start: chunk[0].timestamp,
      end: chunk[chunk.length - 1].timestamp,
      open: chunk[0].price,
      high: Math.max(...chunk.map((p) => p.price)),
      low: Math.min(...chunk.map((p) => p.price)),
      close: chunk[chunk.length - 1].price,
    })
  }
  return candles
}

function CandleSvg({ bars }: { bars: CandleBar[] }) {
  if (!bars.length) {
    return <div className="chart-empty">Waiting for price data…</div>
  }

  const width = 920
  const height = 320
  const margin = { top: 20, right: 20, bottom: 28, left: 56 }
  const innerWidth = width - margin.left - margin.right
  const innerHeight = height - margin.top - margin.bottom
  const high = Math.max(...bars.flatMap((bar) => [bar.high, bar.open, bar.close, bar.low]))
  const low = Math.min(...bars.flatMap((bar) => [bar.high, bar.open, bar.close, bar.low]))
  const range = Math.max(high - low, 0.0001)
  const barWidth = Math.max(8, (innerWidth / bars.length) * 0.55)

  const yFor = (price: number) => margin.top + innerHeight - ((price - low) / range) * innerHeight
  const xFor = (index: number) => margin.left + (innerWidth / bars.length) * (index + 0.5)

  return (
    <div className="candle-shell">
      <svg viewBox={`0 0 ${width} ${height}`} className="candle-svg" role="img" aria-label="Candlestick chart">
        <defs>
          <linearGradient id="bullGrad" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#22c55e" />
            <stop offset="100%" stopColor="#0f766e" />
          </linearGradient>
          <linearGradient id="bearGrad" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#b91c1c" />
          </linearGradient>
        </defs>
        <g opacity="0.18">
          {[0, 1, 2, 3, 4].map((row) => (
            <line
              key={row}
              x1={margin.left}
              x2={width - margin.right}
              y1={margin.top + (innerHeight / 4) * row}
              y2={margin.top + (innerHeight / 4) * row}
              stroke="#94a3b8"
              strokeDasharray="4 8"
            />
          ))}
        </g>
        {bars.map((bar, index) => {
          const bullish = bar.close >= bar.open
          const color = bullish ? 'url(#bullGrad)' : 'url(#bearGrad)'
          const x = xFor(index)
          const highY = yFor(bar.high)
          const lowY = yFor(bar.low)
          const openY = yFor(bar.open)
          const closeY = yFor(bar.close)
          const bodyTop = Math.min(openY, closeY)
          const bodyBottom = Math.max(openY, closeY)
          const bodyHeight = Math.max(2, bodyBottom - bodyTop)
          return (
            <g key={`${bar.start}-${index}`}>
              <line x1={x} x2={x} y1={highY} y2={lowY} stroke={bullish ? '#2dd4bf' : '#f87171'} strokeWidth="2" />
              <rect
                x={x - barWidth / 2}
                y={bodyTop}
                width={barWidth}
                height={bodyHeight}
                rx="3"
                fill={color}
              />
            </g>
          )
        })}
        <text x={margin.left} y={16} className="chart-caption">Open / High / Low / Close</text>
      </svg>
      <div className="chart-axis">
        {bars.slice(0, 6).map((bar) => (
          <span key={bar.start}>{formatClock(bar.end)}</span>
        ))}
      </div>
    </div>
  )
}

export default function PriceChart({
  points = [],
  symbol,
  timeWindow,
  chartMode,
  onTimeWindowChange,
  onModeChange,
}: {
  points: PricePoint[]
  symbol: string
  timeWindow: TimeWindow
  chartMode: ChartMode
  onTimeWindowChange: (value: TimeWindow) => void
  onModeChange: (value: ChartMode) => void
}) {
  const filtered = useMemo(() => filterByWindow(points, timeWindow), [points, timeWindow])
  const labels = filtered.map((point) => formatClock(point.timestamp))
  const prices = filtered.map((point) => point.price)
  const candles = useMemo(() => groupIntoCandles(filtered), [filtered])

  const lineData = {
    labels,
    datasets: [
      {
        label: `${symbol} price`,
        data: prices,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.12)',
        fill: true,
        tension: 0.28,
        pointRadius: 0,
        pointHitRadius: 8,
      },
    ],
  }

  return (
    <div className="price-chart-card">
      <div className="chart-toolbar">
        <div className="chart-title-block">
          <p className="eyebrow">Price action</p>
          <h3>{symbol} live chart</h3>
          <div className="muted">Use the controls to switch between chart styles and different market windows.</div>
        </div>
        <div className="chart-controls">
          <div className="segmented-control">
            {(['line', 'candle'] as ChartMode[]).map((mode) => (
              <button
                key={mode}
                type="button"
                className={chartMode === mode ? 'segmented active' : 'segmented'}
                onClick={() => onModeChange(mode)}
              >
                {mode === 'line' ? 'Line' : 'Candles'}
              </button>
            ))}
          </div>
          <div className="segmented-control">
            {(Object.keys(WINDOW_LABELS) as TimeWindow[]).map((window) => (
              <button
                key={window}
                type="button"
                className={timeWindow === window ? 'segmented active' : 'segmented'}
                onClick={() => onTimeWindowChange(window)}
              >
                {WINDOW_LABELS[window]}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="chart-shell">
        {chartMode === 'line' ? (
          <div className="line-chart-shell">
            {filtered.length === 0 ? (
              <div className="chart-empty">Waiting for price data…</div>
            ) : (
              <Line
                data={lineData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      labels: { color: '#dbeafe' },
                    },
                    tooltip: {
                      callbacks: {
                        title: (items) => items[0]?.label || '',
                        label: (item) => ` ${symbol}: ${Number(item.parsed.y).toFixed(2)}`,
                      },
                    },
                  },
                  scales: {
                    x: {
                      ticks: {
                        color: '#94a3b8',
                        maxTicksLimit: 8,
                        autoSkip: true,
                      },
                      grid: { color: 'rgba(148, 163, 184, 0.12)' },
                    },
                    y: {
                      ticks: {
                        color: '#94a3b8',
                        callback: (value) => Number(value).toFixed(2),
                      },
                      grid: { color: 'rgba(148, 163, 184, 0.12)' },
                    },
                  },
                }}
              />
            )}
          </div>
        ) : (
          <CandleSvg bars={candles} />
        )}
      </div>
    </div>
  )
}
