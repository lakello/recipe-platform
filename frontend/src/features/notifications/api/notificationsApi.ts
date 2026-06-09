import { apiJson, apiFetch } from '@/shared/api/client'

export interface Notification {
  id: string
  type: 'like' | 'comment' | 'reply' | 'follow' | 'moderation'
  actor_id: string | null
  actor_username: string | null
  actor_avatar_url: string | null
  entity_id: string | null
  entity_type: 'recipe' | 'comment' | null
  body: string | null
  is_read: boolean
  created_at: string
}

export interface NotificationPage {
  items: Notification[]
  total: number
  page: number
  size: number
  has_more: boolean
  unread_count: number
}

export interface UnreadCount {
  count: number
}

export const notificationsApi = {
  list: (page = 1, size = 20) =>
    apiJson<NotificationPage>(`/api/notifications?page=${page}&size=${size}`),

  unreadCount: () => apiJson<UnreadCount>('/api/notifications/unread-count'),

  markRead: (id: string) =>
    apiJson<Notification>(`/api/notifications/${id}/read`, { method: 'PATCH' }),

  markAllRead: () =>
    apiFetch('/api/notifications/read-all', { method: 'PATCH' }),
}
