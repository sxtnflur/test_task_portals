import type { RiskLevel } from '../api/types'

const LABELS: Record<RiskLevel, string> = {
  low: 'низкий',
  middle: 'средний',
  high: 'высокий',
}

export function RiskBadge({ level }: { level: RiskLevel | null }) {
  if (level === null) {
    return <span className="badge badge-risk-none">н/д</span>
  }
  return <span className={`badge badge-risk-${level}`}>{LABELS[level]}</span>
}
