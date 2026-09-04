// Mirrors the DTOs in backend/src/presentation/api/dto — verified against a
// running instance of the backend (see frontend/README.md).

export type PortalStatus = 'open' | 'closed'

export type RiskLevel = 'low' | 'middle' | 'high'

export type RiskFactorName = 'high_instability' | 'high_energy' | 'closing_soon'

export type PortalAction =
  | 'open'
  | 'close'
  | 'mark'
  | 'stabilize'
  | 'send_observers'
  | 'take_observers'

export type ChangeLogAction =
  | 'opened'
  | 'closed'
  | 'marked'
  | 'unmarked'
  | 'added_observer'
  | 'taken_observer'
  | 'stabilize'

export interface RiskFactor {
  name: RiskFactorName
  /** Normalized 0..1 level of this specific factor. */
  value: number
}

export interface PortalShortInfo {
  id: number
  name: string
  world_destination: string
  energy: number
  stability: number
  expired_at: string
  expired: boolean
  observers: number
  status: PortalStatus
  /** `null` when the portal is expired: risk cannot be assessed for it. */
  risk_level: RiskLevel | null
  marked: boolean
}

export interface ChangeLogEntry {
  id: string
  portal_id: number
  action: ChangeLogAction
  acted_at: string
  detail: string | null
}

export interface ListPayload<T> {
  result: T[]
  offset: number
  limit: number
  has_more: boolean
}

export interface PortalInfo extends PortalShortInfo {
  risk_value: number
  risk_factors: RiskFactor[]
  recommended_action: PortalAction
  change_logs: ListPayload<ChangeLogEntry>
}

export interface PortalsSummary {
  open: number
  closed: number
  critical: number
  prioritized_portals: PortalShortInfo[]
}

export interface ApiEnvelope<T> {
  ok: boolean
  payload: T | null
  error: { type: string; detail: string } | null
}
