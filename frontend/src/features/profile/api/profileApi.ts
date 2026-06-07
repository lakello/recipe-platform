import { apiJson, ApiError } from '@/shared/api/client'
import { API_BASE_URL } from '@/shared/config/env'

export type UserRole = 'user' | 'admin' | 'superadmin'

export interface UserProfile {
  id: string
  email: string
  username: string
  is_email_verified: boolean
  is_active: boolean
  role: UserRole
  avatar_url: string | null
  created_at: string
  updated_at: string
}

export interface UserPublicRead {
  id: string
  username: string
  avatar_url: string | null
  created_at: string
  followers_count: number
  following_count: number
  is_following: boolean
}

export interface UpdateProfileData {
  username?: string
}

export const profileApi = {
  getMe: async (): Promise<UserProfile> => {
    // Use plain fetch to avoid the auto-redirect-to-login on 401.
    // This endpoint is called on every page to check auth state;
    // unauthenticated is a normal case, not an error worth redirecting for.
    const res = await fetch(`${API_BASE_URL}/api/users/me`, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: 'Unknown error' }))
      throw new ApiError(res.status, body.detail ?? body.message ?? 'Request failed')
    }
    return res.json()
  },

  updateMe: (data: UpdateProfileData) =>
    apiJson<UserProfile>('/api/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  getPublicUser: (userId: string) => apiJson<UserPublicRead>(`/api/users/${userId}`),
}
