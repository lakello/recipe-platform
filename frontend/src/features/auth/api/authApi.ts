import { apiJson } from '@/shared/api/client'

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
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
    apiJson<TokenResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: LoginData) =>
    apiJson<TokenResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  logout: () =>
    apiJson<void>('/api/auth/logout', { method: 'POST' }),
}
