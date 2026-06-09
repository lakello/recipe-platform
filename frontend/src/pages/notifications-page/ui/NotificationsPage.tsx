import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui/Button'
import {
  useMarkAllRead,
  useMarkRead,
  useNotificationPreferences,
  useNotifications,
  useUpdateNotificationPreferences,
} from '@/features/notifications/hooks/useNotifications'
import type { Notification } from '@/features/notifications/api/notificationsApi'

const TYPE_LABELS: Record<string, string> = {
  like: '❤️ Лайк',
  comment: '💬 Комментарий',
  reply: '↩️ Ответ',
  follow: '👤 Подписка',
  moderation: '🔔 Модерация',
}

function notifText(n: Notification): string {
  const actor = n.actor_username ?? 'Система'
  switch (n.type) {
    case 'like':
      return `${actor} поставил лайк вашему рецепту`
    case 'comment':
      return `${actor} прокомментировал ваш рецепт`
    case 'reply':
      return `${actor} ответил на ваш комментарий`
    case 'follow':
      return `${actor} подписался на вас`
    case 'moderation':
      return n.body ?? 'Сообщение от модератора'
  }
}

function notifLink(n: Notification): string | null {
  if (n.entity_type === 'recipe' && n.entity_id) return `/recipes/${n.entity_id}`
  if (n.type === 'follow' && n.actor_id) return `/users/${n.actor_id}`
  return null
}

function NotifRow({ n }: { n: Notification }) {
  const { mutate: markRead } = useMarkRead()
  const link = notifLink(n)
  const text = notifText(n)

  const content = (
    <div
      className={`flex items-start gap-3 px-4 py-3 rounded-lg transition-colors cursor-pointer ${
        !n.is_read ? 'bg-blue-50 hover:bg-blue-100' : 'hover:bg-gray-50'
      }`}
      onClick={() => !n.is_read && markRead(n.id)}
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-800">{text}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-gray-400">
            {TYPE_LABELS[n.type] ?? n.type}
          </span>
          <span className="text-xs text-gray-300">·</span>
          <span className="text-xs text-gray-400">
            {new Date(n.created_at).toLocaleString('ru-RU', {
              day: '2-digit',
              month: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>
      {!n.is_read && (
        <span className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shrink-0" />
      )}
    </div>
  )

  return link ? <Link to={link}>{content}</Link> : content
}

type PrefKey = 'email_like' | 'email_comment' | 'email_follow'

const PREF_ITEMS: { key: PrefKey; label: string }[] = [
  { key: 'email_like', label: 'Email при лайке рецепта' },
  { key: 'email_comment', label: 'Email при комментарии к рецепту' },
  { key: 'email_follow', label: 'Email при новой подписке' },
]

function NotifSettings() {
  const { data: prefs, isPending } = useNotificationPreferences()
  const { mutate: updatePrefs } = useUpdateNotificationPreferences()

  if (isPending) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-5">
        <p className="text-sm text-gray-400">Загрузка настроек...</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-5">
      <h2 className="font-semibold text-gray-900 mb-4">Настройки уведомлений</h2>
      <div className="space-y-3">
        {PREF_ITEMS.map(({ key, label }) => (
          <label key={key} className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={prefs?.[key] ?? true}
              onChange={() => updatePrefs({ [key]: !(prefs?.[key] ?? true) })}
              className="w-4 h-4 rounded text-blue-600"
            />
            <span className="text-sm text-gray-700">{label}</span>
          </label>
        ))}
      </div>
    </div>
  )
}

export function NotificationsPage() {
  const [page, setPage] = useState(1)
  const { data, isPending } = useNotifications(page)
  const { mutate: markAll } = useMarkAllRead()

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/recipes" className="text-sm text-gray-500 hover:text-gray-700">
            ← Назад
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Уведомления</h1>
        </div>
        {data && data.unread_count > 0 && (
          <Button variant="secondary" onClick={() => markAll()}>
            Прочитать все ({data.unread_count})
          </Button>
        )}
      </div>

      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          {isPending && (
            <p className="text-sm text-gray-400 text-center py-10">Загрузка...</p>
          )}
          {data && data.items.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-10">
              Нет уведомлений
            </p>
          )}
          {data && data.items.length > 0 && (
            <div className="divide-y divide-gray-100">
              {data.items.map((n) => (
                <NotifRow key={n.id} n={n} />
              ))}
            </div>
          )}
        </div>

        {data && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">Всего: {data.total}</p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 1}
              >
                ←
              </Button>
              <span className="text-sm text-gray-600 self-center">стр. {page}</span>
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.has_more}
              >
                →
              </Button>
            </div>
          </div>
        )}

        <NotifSettings />
      </div>
    </div>
  )
}
