import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../api/client'
import { getPortals, getPortalsSummary } from '../api/portals'
import type { PortalShortInfo, PortalsSummary } from '../api/types'
import { ErrorBanner } from '../components/ErrorBanner'
import { MarkedBadge } from '../components/MarkedBadge'
import { RiskBadge } from '../components/RiskBadge'
import { StatusBadge } from '../components/StatusBadge'
import { formatExpiresIn } from '../utils/time'

const PAGE_SIZE = 10

export function PortalsListPage() {
  const [offset, setOffset] = useState(0)
  const [portals, setPortals] = useState<PortalShortInfo[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [summary, setSummary] = useState<PortalsSummary | null>(null)
  const [summaryError, setSummaryError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    getPortals(offset, PAGE_SIZE)
      .then((page) => {
        if (cancelled) return
        setPortals(page.result)
        setHasMore(page.has_more)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : 'Не удалось загрузить порталы')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [offset])

  useEffect(() => {
    let cancelled = false
    setSummaryError(null)

    getPortalsSummary()
      .then((result) => {
        if (!cancelled) setSummary(result)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setSummaryError(err instanceof ApiError ? err.message : 'Не удалось загрузить сводку')
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="page">
      <div className="page-header">
        <h1>Порталы</h1>
      </div>

      {summaryError && <ErrorBanner message={summaryError} />}

      {summary && (
        <div className="card">
          <div className="summary-stats">
            <div className="summary-stat">
              <div className="value">{summary.open}</div>
              <div className="label">Открыто</div>
            </div>
            <div className="summary-stat">
              <div className="value">{summary.closed}</div>
              <div className="label">Закрыто</div>
            </div>
            <div className="summary-stat">
              <div className={`value${summary.critical > 0 ? ' danger' : ''}`}>{summary.critical}</div>
              <div className="label">Критических</div>
            </div>
          </div>

          {summary.prioritized_portals.length > 0 && (
            <>
              <div className="detail-field" style={{ marginTop: '1.25rem' }}>
                <div className="label">Приоритетные порталы</div>
              </div>
              <ul className="critical-list">
                {summary.prioritized_portals.map((portal) => (
                  <li key={portal.id}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Link to={`/portals/${portal.id}`}>
                        {portal.name} <span className="muted">#{portal.id}</span>
                      </Link>
                      {portal.marked && <MarkedBadge />}
                    </span>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.75rem' }}>
                      <RiskBadge level={portal.risk_level} />
                      <span className="muted">
                        {portal.expired ? 'истёк' : formatExpiresIn(portal.expired_at)}
                      </span>
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      {error && <ErrorBanner message={error} />}

      {loading ? (
        <div className="loading">Загрузка порталов…</div>
      ) : portals.length === 0 ? (
        <div className="empty-state">Нет порталов для отображения.</div>
      ) : (
        <div className="card" style={{ padding: 0, overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Название</th>
                <th>Мир назначения</th>
                <th>Статус</th>
                <th>Энергия</th>
                <th>Стабильность</th>
                <th>Риск</th>
                <th>Наблюдатели</th>
                <th>Истекает через</th>
              </tr>
            </thead>
            <tbody>
              {portals.map((portal) => (
                <tr key={portal.id}>
                  <td>{portal.id}</td>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Link to={`/portals/${portal.id}`}>{portal.name}</Link>
                      {portal.marked && <MarkedBadge />}
                    </span>
                  </td>
                  <td>{portal.world_destination}</td>
                  <td>
                    <StatusBadge status={portal.status} />
                  </td>
                  <td>{portal.energy}</td>
                  <td>{portal.stability.toFixed(1)}</td>
                  <td>
                    <RiskBadge level={portal.risk_level} />
                  </td>
                  <td>{portal.observers}</td>
                  <td>{portal.expired ? 'истёк' : formatExpiresIn(portal.expired_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <button onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))} disabled={offset === 0 || loading}>
          ← Назад
        </button>
        <span>
          Показано {portals.length === 0 ? 0 : offset + 1}–{offset + portals.length}
        </span>
        <button onClick={() => setOffset((o) => o + PAGE_SIZE)} disabled={!hasMore || loading}>
          Далее →
        </button>
      </div>
    </div>
  )
}
