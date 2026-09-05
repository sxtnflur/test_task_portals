import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../api/client'
import {
  addObserver,
  closePortal,
  filterLogsForPortal,
  getPortal,
  markPortal,
  openPortal,
  stabilizePortal,
  takeObserver,
  unmarkPortal,
} from '../api/portals'
import type { ChangeLogEntry, PortalInfo } from '../api/types'
import { ErrorBanner } from '../components/ErrorBanner'
import { MarkedBadge } from '../components/MarkedBadge'
import { RiskBadge } from '../components/RiskBadge'
import { StatusBadge } from '../components/StatusBadge'
import { formatExpiresIn, parseUtcDate } from '../utils/time'

const REFRESH_CHECK_INTERVAL_MS = 60_000
const SKIP_REFRESH_IF_FETCHED_WITHIN_MS = 10_000

type ActionKey = 'open' | 'close' | 'mark' | 'unmark' | 'stabilize' | 'addObserver' | 'takeObserver'

const RISK_FACTOR_LABELS: Record<string, string> = {
  high_instability: 'высокая нестабильность',
  high_energy: 'высокая энергия',
  closing_soon: 'скорое закрытие',
}

const PORTAL_ACTION_LABELS: Record<string, string> = {
  nothing: 'ничего не требуется',
  open: 'открыть',
  close: 'закрыть',
  mark: 'пометить как «под вопросом»',
  stabilize: 'стабилизировать',
  add_observers: 'отправить наблюдателей',
  send_observers: 'отправить наблюдателей',
  take_observers: 'отозвать наблюдателей',
}

const CHANGE_LOG_ACTION_LABELS: Record<string, string> = {
  opened: 'открыт',
  closed: 'закрыт',
  marked: 'отмечен «под вопросом»',
  unmarked: 'снята отметка «под вопросом»',
  added_observer: 'добавлен наблюдатель',
  taken_observer: 'отозван наблюдатель',
  stabilize: 'стабилизация',
}

function translate(labels: Record<string, string>, key: string): string {
  return labels[key] ?? key.replace(/_/g, ' ')
}

export function PortalDetailPage() {
  const { id } = useParams<{ id: string }>()
  const portalId = Number(id)

  const [portal, setPortal] = useState<PortalInfo | null>(null)
  const [logs, setLogs] = useState<ChangeLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [pendingAction, setPendingAction] = useState<ActionKey | null>(null)
  const lastFetchedAtRef = useRef(0)

  const load = useCallback(() => {
    lastFetchedAtRef.current = Date.now()
    setLoading(true)
    setLoadError(null)
    return getPortal(portalId)
      .then((info) => {
        setPortal(info)
        setLogs(filterLogsForPortal(info.change_logs, portalId))
      })
      .catch((err: unknown) => {
        setLoadError(err instanceof ApiError ? err.message : 'Не удалось загрузить портал')
      })
      .finally(() => setLoading(false))
  }, [portalId])

  useEffect(() => {
    load()
  }, [load])

  // Keep the portal's state (and the "expires in" countdown) from going
  // stale: every minute, refetch it - but only if nothing else (an action,
  // the initial load) already fetched it in the last 10 seconds.
  useEffect(() => {
    const interval = setInterval(() => {
      if (Date.now() - lastFetchedAtRef.current >= SKIP_REFRESH_IF_FETCHED_WITHIN_MS) {
        load()
      }
    }, REFRESH_CHECK_INTERVAL_MS)

    return () => clearInterval(interval)
  }, [load])

  async function runAction(key: ActionKey, fn: () => Promise<unknown>) {
    setPendingAction(key)
    setActionError(null)
    try {
      await fn()
      await load()
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : 'Действие не выполнено')
    } finally {
      setPendingAction(null)
    }
  }

  if (loading && !portal) {
    return (
      <div className="page">
        <BackLink />
        <div className="loading">Загрузка портала…</div>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="page">
        <BackLink />
        <ErrorBanner message={loadError} />
      </div>
    )
  }

  if (!portal) {
    return null
  }

  const isOpen = portal.status === 'open'
  const isClosed = portal.status === 'closed'
  const isBusy = pendingAction !== null

  return (
    <div className="page">
      <BackLink />

      <div className="page-header">
        <h1>
          {portal.name} <span className="muted">#{portal.id}</span>
        </h1>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <StatusBadge status={portal.status} />
          {portal.marked && <MarkedBadge />}
        </div>
      </div>

      {actionError && <ErrorBanner message={actionError} />}

      <div className="card">
        <div className="detail-grid">
          <Field label="Мир назначения" value={portal.world_destination} />
          <Field label="Энергия" value={portal.energy} />
          <Field label="Стабильность" value={portal.stability.toFixed(1)} />
          <Field label="Наблюдатели" value={portal.observers} />
          <Field
            label="Истекает через"
            value={portal.expired ? 'истёк' : formatExpiresIn(portal.expired_at)}
          />
          <Field label="Уровень риска" value={<RiskBadge level={portal.risk_level} />} />
          <Field label="Оценка риска" value={`${portal.risk_value} / 10`} />
        </div>

        {portal.risk_factors.length > 0 && (
          <>
            <div className="detail-field" style={{ marginTop: '1.25rem' }}>
              <div className="label">Факторы риска</div>
            </div>
            <div className="risk-factor-list">
              {portal.risk_factors.map((factor) => (
                <div className="risk-factor" key={factor.name}>
                  <span style={{ minWidth: 130 }}>{translate(RISK_FACTOR_LABELS, factor.name)}</span>
                  <span className="bar-track">
                    <span className="bar-fill" style={{ width: `${Math.round(factor.value * 100)}%` }} />
                  </span>
                  <span className="muted">{Math.round(factor.value * 100)}%</span>
                </div>
              ))}
            </div>
          </>
        )}

        <div style={{ marginTop: '1.25rem' }}>
          <span className="recommended-action">
            Рекомендация: {translate(PORTAL_ACTION_LABELS, portal.recommended_action)}
          </span>
        </div>
      </div>

      <div className="card">
        <div className="detail-field" style={{ marginBottom: '0.9rem' }}>
          <div className="label">Действия</div>
        </div>
        <div className="actions-grid">
          <button
            className="primary"
            disabled={isBusy || isOpen}
            onClick={() => runAction('open', () => openPortal(portal.id))}
          >
            {pendingAction === 'open' ? 'Открытие…' : 'Открыть'}
          </button>
          <button
            className="danger"
            disabled={isBusy || isClosed || portal.observers > 0}
            title={portal.observers > 0 ? 'Нельзя закрыть портал, пока внутри есть наблюдатели' : undefined}
            onClick={() => runAction('close', () => closePortal(portal.id))}
          >
            {pendingAction === 'close' ? 'Закрытие…' : 'Закрыть'}
          </button>
          <button
            disabled={isBusy || isClosed}
            onClick={() => runAction('stabilize', () => stabilizePortal(portal.id))}
          >
            {pendingAction === 'stabilize' ? 'Стабилизация…' : 'Стабилизировать (+0.5)'}
          </button>
          <button
            disabled={isBusy || isClosed}
            onClick={() => runAction('addObserver', () => addObserver(portal.id))}
          >
            {pendingAction === 'addObserver' ? 'Отправка…' : 'Отправить наблюдателя'}
          </button>
          <button
            disabled={isBusy || portal.observers === 0}
            onClick={() => runAction('takeObserver', () => takeObserver(portal.id))}
          >
            {pendingAction === 'takeObserver' ? 'Отзыв…' : 'Отозвать наблюдателя'}
          </button>
          {portal.marked ? (
            <button disabled={isBusy} onClick={() => runAction('unmark', () => unmarkPortal(portal.id))}>
              {pendingAction === 'unmark' ? 'Снятие отметки…' : 'Убрать отметку «под вопросом»'}
            </button>
          ) : (
            <button disabled={isBusy} onClick={() => runAction('mark', () => markPortal(portal.id))}>
              {pendingAction === 'mark' ? 'Отметка…' : 'Пометить как «под вопросом»'}
            </button>
          )}
        </div>
      </div>

      <div className="card">
        <div className="detail-field" style={{ marginBottom: '0.9rem' }}>
          <div className="label">Журнал изменений</div>
        </div>
        {logs.length === 0 ? (
          <div className="empty-state">Для этого портала нет записей об изменениях.</div>
        ) : (
          <ul className="change-log-list">
            {logs.map((log) => (
              <li key={log.id}>
                <span>
                  {translate(CHANGE_LOG_ACTION_LABELS, log.action)}
                  {log.detail ? ` — ${log.detail}` : ''}
                </span>
                <span className="muted">{parseUtcDate(log.acted_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function BackLink() {
  return (
    <Link to="/" className="back-link">
      ← Назад к порталам
    </Link>
  )
}

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="detail-field">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  )
}
