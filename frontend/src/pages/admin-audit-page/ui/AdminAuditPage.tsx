import { useState } from 'react'
import { AdminLayout } from '@/widgets/admin-layout'
import { useAuditLog } from '@/features/admin/hooks/useAdmin'
import { Button } from '@/shared/ui/Button'

const ACTION_LABELS: Record<string, string> = {
  hide_recipe: 'Скрыл рецепт',
  unhide_recipe: 'Показал рецепт',
  hide_comment: 'Скрыл комментарий',
  unhide_comment: 'Показал комментарий',
  block_user: 'Заблокировал пользователя',
  unblock_user: 'Разблокировал пользователя',
  assign_role: 'Назначил роль',
  resolve_report: 'Принял жалобу',
  dismiss_report: 'Отклонил жалобу',
}

export function AdminAuditPage() {
  const [page, setPage] = useState(1)
  const { data, isPending, error } = useAuditLog(page)

  return (
    <AdminLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Журнал действий</h1>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {data && (
        <>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Действие</th>
                  <th className="px-4 py-3">Цель</th>
                  <th className="px-4 py-3">Причина</th>
                  <th className="px-4 py-3">Дата</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((entry) => (
                  <tr key={entry.id} className="border-b border-gray-100 last:border-0">
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-gray-800">
                        {ACTION_LABELS[entry.action_type] ?? entry.action_type}
                      </p>
                      <p className="text-xs text-gray-400">
                        {entry.moderator_id.slice(0, 8)}…
                      </p>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {entry.target_type} · {entry.target_id.slice(0, 8)}…
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {entry.reason ?? '—'}
                      {entry.meta && entry.action_type === 'assign_role' && (
                        <span className="text-xs text-gray-400 block">
                          {(entry.meta as Record<string, string>).old_role} → {(entry.meta as Record<string, string>).new_role}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-400">
                      {new Date(entry.created_at).toLocaleString('ru-RU')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {data.items.length === 0 && (
              <p className="text-center text-gray-500 py-8">Действий пока нет.</p>
            )}
          </div>

          <div className="flex items-center justify-between mt-4">
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
        </>
      )}
    </AdminLayout>
  )
}
