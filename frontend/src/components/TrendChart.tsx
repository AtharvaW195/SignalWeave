import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

interface TrendPoint {
  label: string
  score: number
  latency: number
}

interface TrendChartProps {
  data: TrendPoint[]
}

export function TrendChart({ data }: TrendChartProps) {
  return (
    <div className="panel chart-panel">
      <div className="panel-header">
        <h2>Anomaly Trend</h2>
        <p>Rolling view of decision scores and end-to-end latency.</p>
      </div>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <XAxis dataKey="label" hide />
            <YAxis domain={[0, 1]} tick={{ fill: '#9fb0c9' }} />
            <Tooltip
              contentStyle={{ background: '#08111d', border: '1px solid rgba(145, 170, 200, 0.16)', color: '#f4f7fb' }}
            />
            <Line type="monotone" dataKey="score" stroke="#2dd4bf" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="latency" stroke="#f59e0b" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
