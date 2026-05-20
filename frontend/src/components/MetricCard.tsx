interface MetricCardProps {
  label: string
  value: string
  detail: string
  tone?: 'cyan' | 'amber' | 'emerald' | 'rose'
}

export function MetricCard({ label, value, detail, tone = 'cyan' }: MetricCardProps) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <span className="metric-label">{label}</span>
      <strong className="metric-value">{value}</strong>
      <span className="metric-detail">{detail}</span>
    </article>
  )
}
