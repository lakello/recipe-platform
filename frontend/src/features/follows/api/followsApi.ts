import { apiJson, apiFetch } from '@/shared/api/client'

export interface FollowUser {
  id: string
  username: string
  avatar_url: string | null
  is_following: boolean
}

export interface FollowUserPage {
  items: FollowUser[]
  total: number
  page: number
  size: number
  has_more: boolean
}

export const followsApi = {
  follow: async (userId: string) => {
    const res = await apiFetch(`/api/users/${userId}/follow`, { method: 'POST' })
    if (!res.ok && res.status !== 409) throw new Error('Не удалось подписаться')
  },

  unfollow: async (userId: string) => {
    const res = await apiFetch(`/api/users/${userId}/follow`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Не удалось отписаться')
  },

  listFollowers: (userId: string, page = 1, size = 20) =>
    apiJson<FollowUserPage>(
      `/api/users/${userId}/followers?page=${page}&size=${size}`,
    ),

  listFollowing: (userId: string, page = 1, size = 20) =>
    apiJson<FollowUserPage>(
      `/api/users/${userId}/following?page=${page}&size=${size}`,
    ),
}
