import { api } from './client'
import type { ChangeLogEntry, ListPayload, PortalAction, PortalInfo, PortalShortInfo, PortalsSummary } from './types'

export function getPortals(offset: number, limit: number) {
  return api.get<ListPayload<PortalShortInfo>>(`/portals?offset=${offset}&limit=${limit}`)
}

export function getPortalsSummary() {
  return api.get<PortalsSummary>('/portals/summary')
}

export function getPortal(portalId: number) {
  return api.get<PortalInfo>(`/portals/${portalId}`)
}

export function getRecommendedAction(portalId: number) {
  return api.get<{ action: PortalAction }>(`/portals/${portalId}/recommendedAction`)
}

export function openPortal(portalId: number) {
  return api.post<null>('/portals/open', { portal_id: portalId })
}

export function closePortal(portalId: number) {
  return api.post<null>('/portals/close', { portal_id: portalId })
}

export function stabilizePortal(portalId: number) {
  return api.post<{ stability: number }>('/portals/stabilize', { portal_id: portalId })
}

export function addObserver(portalId: number) {
  return api.post<{ observers_count: number }>('/portals/observers/add', { portal_id: portalId })
}

export function takeObserver(portalId: number) {
  return api.post<{ observers_count: number }>('/portals/observers/take', { portal_id: portalId })
}

export function markPortal(portalId: number) {
  return api.post<null>('/portals/mark', { portal_id: portalId })
}

export function unmarkPortal(portalId: number) {
  return api.post<null>('/portals/unmark', { portal_id: portalId })
}

/**
 * The backend's `/logs/portal` list is global, not scoped by portal (a
 * limitation of the current `PortalChangeLogsRepository` port - it has no
 * portal_id filter). `PortalInfo.change_logs` inherits the same limitation.
 * We ask for a generously large page and filter client-side as a
 * workaround; it's not a substitute for real server-side filtering once
 * the backend supports it.
 */
export function filterLogsForPortal(logs: ListPayload<ChangeLogEntry>, portalId: number): ChangeLogEntry[] {
  return logs.result.filter((log) => log.portal_id === portalId)
}
