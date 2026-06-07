import { apiJson } from '@/shared/api/client'

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
}

export interface UpdateProfileData {
  username?: string
}

export const profileApi = {
  getMe: () => apiJson<UserProfile>('/api/users/me'),

  updateMe: (data: UpdateProfileData) =>
    apiJson<UserProfile>('/api/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  getPublicUser: (userId: string) => apiJson<UserPublicRead>(`/api/users/${userId}`),
}
