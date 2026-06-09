import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMarkAllRead, useMarkRead, useNotifications, useUnreadCount } from '../hooks/useNotifications'
import type { Notification } from '../api/notificationsApi'

function notifText(n: Notification): string {
  const actor = n.actor_username ?? 'Система'
  switch (n.type) {
    case 'like': return `${actor} поставил лайк вашему рецепту`
    case 'comment': return `${actor} прокомментировал ваш рецепт`
    case 'reply': return `${actor} ответил на ваш комментарий`
    case 'follow': return `${actor} подписался на вас`
    case 'moderation': return n.body ?? 'Сообщение от модератора'
  }
}

function notifLink(n: Notification): string | null {
  if (n.entity_type === 'recipe' && n.entity_id) return `/recipes/${n.entity_id}`
  if (n.type === 'follow' && n.actor_id) return `/users/${n.actor_id}`
  return null
}

function NotifItem({ n, onRead }: { n: Notification; onRead: (id: string) => void }) {
  const link = notifLink(n)
  const text = notifText(n)
  const time = new Date(n.created_at).toLocaleDateString('ru-RU')

  const inner = (
    <div
      className={`px-4 py-3 hover:bg-gray-50 cursor-pointer ${!n.is_read ? 'bg-blue-50' : ''}`}
      onClick={() => !n.is_read && onRead(n.id)}
    >
      <p className="text-sm text-gray-800 leading-snug">{text}</p>
      <p className="text-xs text-gray-400 mt-0.5">{time}</p>
    </div>
  )

  return link ? <Link to={link}>{inner}</Link> : inner
}

export function NotificationBell() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const { data: unread } = useUnreadCount()
  const { data, isPending } = useNotifications(1)
  const { mutate: markRead } = useMarkRead()
  const { mutate: markAll } = useMarkAllRead()

  const count = unread?.count ?? 0

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-full hover:bg-gray-100 transition-colors"
        aria-label="Уведомления"
      >
        <svg
          className="w-6 h-6 text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        {count > 0 && (
          <span className="absolute top-1 right-1 min-w-[16px] h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center px-0.5">
            {count > 99 ? '99+' : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-200 z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <span className="text-sm font-semibold text-gray-900">Уведомления</span>
            <div className="flex gap-2">
              {count > 0 && (
                <button
                  onClick={() => markAll()}
                  className="text-xs text-blue-600 hover:underline"
                >
                  Прочитать все
                </button>
              )}
              <Link
                to="/notifications"
                className="text-xs text-gray-400 hover:text-gray-600"
                onClick={() => setOpen(false)}
              >
                Все →
              </Link>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-gray-100">
            {isPending && (
              <p className="text-sm text-gray-400 px-4 py-6 text-center">Загрузка...</p>
            )}
            {data && data.items.length === 0 && (
              <p className="text-sm text-gray-400 px-4 py-6 text-center">
                Нет уведомлений
              </p>
            )}
            {data?.items.map((n) => (
              <NotifItem
                key={n.id}
                n={n}
                onRead={(id) => {
                  markRead(id)
                  setOpen(false)
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
