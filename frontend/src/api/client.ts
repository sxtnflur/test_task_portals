import type { ApiEnvelope } from './types'

const BASE_URL = '/api/v1'

/**
 * Raised for both of the backend's error shapes:
 *  - the custom envelope (`{ok:false, error:{type, detail}}`) used for
 *    domain/not-found errors (400/404),
 *  - FastAPI's own request-validation shape (`{detail: [...]}`, 422),
 *    which the backend does not wrap in the custom envelope.
 */
export class ApiError extends Error {
  readonly status: number
  readonly type: string | null

  constructor(status: number, message: string, type: string | null = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.type = type
  }
}

function messageFromValidationError(body: unknown): string {
  if (
    body &&
    typeof body === 'object' &&
    'detail' in body &&
    Array.isArray((body as { detail: unknown }).detail)
  ) {
    const details = (body as { detail: Array<{ msg?: string; loc?: unknown[] }> }).detail
    return details
      .map((d) => (d.loc ? `${d.loc.join('.')}: ${d.msg ?? ''}` : d.msg ?? ''))
      .filter(Boolean)
      .join('; ') || 'Некорректный запрос'
  }
  return 'Некорректный запрос'
}

async function request<TPayload>(path: string, init?: RequestInit): Promise<TPayload> {
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: {
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers,
      },
    })
  } catch {
    throw new ApiError(0, 'Не удаётся подключиться к серверу. Он запущен?')
  }

  let body: unknown = null
  try {
    body = await response.json()
  } catch {
    // No/invalid JSON body - fall through, handled per status below.
  }

  if (response.status === 422) {
    throw new ApiError(422, messageFromValidationError(body))
  }

  const envelope = body as ApiEnvelope<TPayload> | null

  if (!response.ok || !envelope || envelope.ok === false) {
    const detail = envelope?.error?.detail ?? `Запрос завершился с ошибкой, статус ${response.status}`
    throw new ApiError(response.status, detail, envelope?.error?.type ?? null)
  }

  return envelope.payload as TPayload
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
}
