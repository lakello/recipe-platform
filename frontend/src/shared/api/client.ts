import { API_BASE_URL } from '@/shared/config/env'

let isRefreshing = false

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function fetchWithCredentials(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    credentials: 'include',
    ...init,
  })
}

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetchWithCredentials(path, init)

  if (response.status === 401 && !path.includes('/auth/refresh') && !isRefreshing) {
    isRefreshing = true
    try {
      const refreshed = await fetchWithCredentials('/api/auth/refresh', {
        method: 'POST',
      })
      if (refreshed.ok) {
        return fetchWithCredentials(path, init)
      }
    } finally {
      isRefreshing = false
    }
  }

  return response
}

export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await apiFetch(path, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiError(res.status, body.detail ?? body.message ?? 'Request failed')
  }
  return res.json() as Promise<T>
}
