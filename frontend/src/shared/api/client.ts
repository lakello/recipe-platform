import { API_BASE_URL } from '@/shared/config/env'

const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS'])
const TRANSIENT_STATUSES = new Set([429, 502, 503, 504])
let refreshPromise: Promise<boolean> | null = null
let logoutPromise: Promise<void> | null = null

function csrfToken(): string | undefined {
  const cookie = document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrf_token='))
  return cookie ? decodeURIComponent(cookie.slice('csrf_token='.length)) : undefined
}

export class ApiError extends Error {
  status: number
  kind: ApiErrorKind
  details?: unknown

  constructor(status: number, message: string, details?: unknown) {
    super(message)
    this.status = status
    this.kind = errorKind(status)
    this.details = details
  }
}

export type ApiErrorKind =
  | 'validation'
  | 'unauthorized'
  | 'forbidden'
  | 'rate_limit'
  | 'unavailable'
  | 'offline'
  | 'unknown'

function errorKind(status: number): ApiErrorKind {
  if (status === 0) return 'offline'
  if (status === 401) return 'unauthorized'
  if (status === 403) return 'forbidden'
  if (status === 422) return 'validation'
  if (status === 429) return 'rate_limit'
  if ([502, 503, 504].includes(status)) return 'unavailable'
  return 'unknown'
}

async function fetchWithCredentials(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const headers = new Headers(init?.headers)
  headers.set('Content-Type', 'application/json')
  const method = (init?.method ?? 'GET').toUpperCase()
  const csrf = csrfToken()
  if (csrf && !SAFE_METHODS.has(method)) headers.set('X-CSRF-Token', csrf)
  return fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  })
}

function refresh(): Promise<boolean> {
  refreshPromise ??= fetchWithCredentials('/api/auth/refresh', {
    method: 'POST',
  })
    .then((response) => response.ok)
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}

function logoutOnce(): Promise<void> {
  logoutPromise ??= Promise.resolve().then(() => {
    window.location.assign('/login')
  })
  return logoutPromise
}

export async function apiFetch(
  path: string,
  init?: RequestInit,
  retried = false,
): Promise<Response> {
  const method = (init?.method ?? 'GET').toUpperCase()
  let response: Response
  try {
    response = await fetchWithCredentials(path, init)
  } catch {
    if (!retried && SAFE_METHODS.has(method)) {
      return apiFetch(path, init, true)
    }
    throw new ApiError(0, 'Нет подключения к сети')
  }

  if (response.status === 401 && !path.includes('/auth/refresh') && !retried) {
    if (await refresh()) return apiFetch(path, init, true)
    await logoutOnce()
  } else if (
    !retried &&
    SAFE_METHODS.has(method) &&
    TRANSIENT_STATUSES.has(response.status)
  ) {
    return apiFetch(path, init, true)
  }

  return response
}

export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await apiFetch(path, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiError(
      res.status,
      typeof body.detail === 'string'
        ? body.detail
        : (body.message ?? 'Request failed'),
      body.detail,
    )
  }
  return res.json() as Promise<T>
}
