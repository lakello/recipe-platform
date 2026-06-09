import { useState } from 'react'
import { AdminLayout } from '@/widgets/admin-layout'
import { useAdminComments } from '@/features/admin/hooks/useAdmin'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiJson } from '@/shared/api/client'
import type { AdminComment } from '@/features/admin/api/adminApi'
import { Button } from '@/shared/ui/Button'

function useToggleComment(commentId: string, hidden: boolean) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () =>
      apiJson(`/api/comments/${commentId}/${hidden ? 'unhide' : 'hide'}`, {
        method: 'POST',
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'comments'] }),
  })
}

function CommentRow({ comment }: { comment: AdminComment }) {
  const { mutate: toggle, isPending } = useToggleComment(comment.id, comment.is_hidden)

  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="py-3 pr-4 max-w-xs">
        <p className="text-sm text-gray-800 truncate">{comment.body}</p>
        <p className="text-xs text-gray-400 mt-0.5">
          {new Date(comment.created_at).toLocaleDateString('ru-RU')}
        </p>
      </td>
      <td className="py-3 pr-4">
        <div className="flex flex-col gap-1">
          {comment.is_hidden && (
            <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-red-100 text-red-700 w-fit">
              скрыт
            </span>
          )}
          {comment.is_deleted && (
            <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-500 w-fit">
              удалён
            </span>
          )}
          {!comment.is_hidden && !comment.is_deleted && (
            <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-green-100 text-green-700 w-fit">
              виден
            </span>
          )}
        </div>
      </td>
      <td className="py-3 text-right">
        {!comment.is_deleted && (
          <Button
            variant={comment.is_hidden ? 'secondary' : 'danger'}
            loading={isPending}
            onClick={() => toggle()}
          >
            {comment.is_hidden ? 'Показать' : 'Скрыть'}
          </Button>
        )}
      </td>
    </tr>
  )
}

export function AdminCommentsPage() {
  const [page, setPage] = useState(1)
  const { data, isPending, error } = useAdminComments(page)

  return (
    <AdminLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Комментарии</h1>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {data && (
        <>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Комментарий</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="px-4">
                {data.items.map((c) => (
                  <CommentRow key={c.id} comment={c} />
                ))}
              </tbody>
            </table>
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
