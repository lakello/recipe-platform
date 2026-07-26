import { apiFetch, apiJson } from '@/shared/api/client'

export interface WebAuthResponse {
  csrf_token: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
}

export interface LoginData {
  email: string
  password: string
}

export const authApi = {
  register: (data: RegisterData) =>
    apiJson<WebAuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: LoginData) =>
    apiJson<WebAuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  logout: async () => {
    const response = await apiFetch('/api/auth/logout', { method: 'POST' })
    if (!response.ok) throw new Error('Не удалось выйти')
  },
}
