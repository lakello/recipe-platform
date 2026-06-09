import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { notificationsApi } from '../api/notificationsApi'

const KEYS = {
  list: (page: number) => ['notifications', page] as const,
  unread: () => ['notifications', 'unread'] as const,
}

export function useNotifications(page = 1) {
  return useQuery({
    queryKey: KEYS.list(page),
    queryFn: () => notificationsApi.list(page),
  })
}

export function useUnreadCount(enabled = true) {
  return useQuery({
    queryKey: KEYS.unread(),
    queryFn: notificationsApi.unreadCount,
    refetchInterval: 30_000,
    enabled,
  })
}

export function useMarkRead() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useMarkAllRead() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}
