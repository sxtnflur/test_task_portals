import type { PortalStatus } from '../api/types'

const LABELS: Record<PortalStatus, string> = {
  open: 'открыт',
  closed: 'закрыт',
}

export function StatusBadge({ status }: { status: PortalStatus }) {
  return <span className={`badge badge-${status}`}>{LABELS[status]}</span>
}
