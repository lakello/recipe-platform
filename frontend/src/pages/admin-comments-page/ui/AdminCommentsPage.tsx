import { useState } from 'react'
import { Link } from 'react-router-dom'
import { AdminLayout } from '@/widgets/admin-layout'
import {
  useAdminRecipes,
  useAdminComments,
  useHideRecipe,
  useUnhideRecipe,
  useDeleteCommentAdmin,
  useHideCommentAdmin,
  useUnhideCommentAdmin,
} from '@/features/admin/hooks/useAdmin'
import type { AdminComment, AdminRecipe } from '@/features/admin/api/adminApi'
import { Button } from '@/shared/ui/Button'

const STATUS_OPTIONS = [
  { value: '', label: 'Все' },
  { value: 'visible', label: 'Видимые' },
  { value: 'hidden', label: 'Скрытые' },
  { value: 'deleted', label: 'Удалённые' },
]

function statusBadge(c: AdminComment) {
  if (c.is_deleted)
    return <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">удалён</span>
  if (c.is_hidden)
    return <span className="text-xs px-1.5 py-0.5 rounded bg-red-100 text-red-700">скрыт</span>
  return <span className="text-xs px-1.5 py-0.5 rounded bg-green-100 text-green-700">виден</span>
}

function CommentRow({ comment }: { comment: AdminComment }) {
  const { mutate: hide, isPending: isHiding } = useHideCommentAdmin()
  const { mutate: unhide, isPending: isUnhiding } = useUnhideCommentAdmin()
  const { mutate: del, isPending: isDeleting } = useDeleteCommentAdmin()

  return (
    <div
      className={`flex items-start gap-3 py-2 px-3 rounded-lg ${
        comment.parent_id ? 'ml-6 border-l-2 border-gray-100 pl-4' : ''
      }`}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <Link
            to={`/users/${comment.author_id}`}
            className="text-xs font-medium text-gray-700 hover:underline"
          >
            {comment.author.username}
          </Link>
          {statusBadge(comment)}
        </div>
        <p
          className={`text-sm ${
            comment.is_deleted || comment.is_hidden
              ? 'text-gray-400 italic'
              : 'text-gray-800'
          } line-clamp-2`}
        >
          {comment.body}
        </p>
      </div>
      <div className="flex gap-1 shrink-0 items-center">
        {!comment.is_deleted && (
          <>
            {comment.is_hidden ? (
              <Button variant="secondary" loading={isUnhiding} onClick={() => unhide(comment.id)}>
                Показать
              </Button>
            ) : (
              <Button variant="danger" loading={isHiding} onClick={() => hide(comment.id)}>
                Скрыть
              </Button>
            )}
            <Button
              variant="danger"
              loading={isDeleting}
              onClick={() => {
                if (confirm('Удалить комментарий?')) del(comment.id)
              }}
            >
              Удалить
            </Button>
          </>
        )}
      </div>
    </div>
  )
}

function buildTree(comments: AdminComment[]) {
  const roots: AdminComment[] = []
  const byId: Record<string, AdminComment & { replies: AdminComment[] }> = {}
  for (const c of comments) {
    byId[c.id] = { ...c, replies: [] }
  }
  for (const c of comments) {
    if (c.parent_id && byId[c.parent_id]) {
      byId[c.parent_id].replies.push(byId[c.id])
    } else {
      roots.push(byId[c.id])
    }
  }
  return roots.map((r) => byId[r.id])
}

function RecipeAccordionRow({
  recipe,
  commentSearch,
  commentStatus,
}: {
  recipe: AdminRecipe
  commentSearch: string
  commentStatus: string
}) {
  const [open, setOpen] = useState(false)
  const { mutate: hide, isPending: isHiding } = useHideRecipe()
  const { mutate: unhide, isPending: isUnhiding } = useUnhideRecipe()
  const { data: commentsData, isPending: commentsLoading } = useAdminComments(
    open ? recipe.id : undefined,
    commentSearch || undefined,
    commentStatus || undefined,
    open,
  )

  const tree = commentsData ? buildTree(commentsData.items) : []

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden mb-3">
      {/* Recipe header row */}
      <div
        className="flex items-center gap-3 px-4 py-3 bg-white hover:bg-gray-50 cursor-pointer select-none"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="text-gray-400 text-sm w-4">{open ? '▾' : '▸'}</span>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 truncate">{recipe.title}</p>
          <p className="text-xs text-gray-400">
            {recipe.author.username} · {recipe.author.email}
          </p>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${
            recipe.is_hidden ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
          }`}
        >
          {recipe.is_hidden ? 'скрыт' : 'виден'}
        </span>
        <div className="shrink-0" onClick={(e) => e.stopPropagation()}>
          {recipe.is_hidden ? (
            <Button variant="secondary" loading={isUnhiding} onClick={() => unhide(recipe.id)}>
              Показать
            </Button>
          ) : (
            <Button
              variant="danger"
              loading={isHiding}
              onClick={() => {
                if (confirm(`Скрыть рецепт "${recipe.title}"?`)) hide({ recipeId: recipe.id })
              }}
            >
              Скрыть
            </Button>
          )}
        </div>
      </div>

      {/* Comments */}
      {open && (
        <div className="border-t border-gray-100 bg-gray-50 px-4 py-3">
          {commentsLoading && <p className="text-sm text-gray-400">Загрузка комментариев...</p>}
          {!commentsLoading && tree.length === 0 && (
            <p className="text-sm text-gray-400">Комментариев нет.</p>
          )}
          <div className="flex flex-col gap-2">
            {tree.map((root) => (
              <div key={root.id}>
                <CommentRow comment={root} />
                {root.replies?.map((reply) => (
                  <CommentRow key={reply.id} comment={reply} />
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export function AdminCommentsPage() {
  const [page, setPage] = useState(1)
  const [recipeSearch, setRecipeSearch] = useState('')
  const [commentSearch, setCommentSearch] = useState('')
  const [commentStatus, setCommentStatus] = useState('')

  const { data: recipesData, isPending, error } = useAdminRecipes(page, recipeSearch || undefined, true)

  const handleRecipeSearch = (v: string) => {
    setRecipeSearch(v)
    setPage(1)
  }

  return (
    <AdminLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Комментарии</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <input
          type="text"
          placeholder="Поиск рецепта по названию или автору..."
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1 min-w-48"
          value={recipeSearch}
          onChange={(e) => handleRecipeSearch(e.target.value)}
        />
        <input
          type="text"
          placeholder="Поиск по тексту комментария..."
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1 min-w-48"
          value={commentSearch}
          onChange={(e) => setCommentSearch(e.target.value)}
        />
        <select
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          value={commentStatus}
          onChange={(e) => setCommentStatus(e.target.value)}
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {recipesData && (
        <>
          {recipesData.items.map((recipe) => (
            <RecipeAccordionRow
              key={recipe.id}
              recipe={recipe}
              commentSearch={commentSearch}
              commentStatus={commentStatus}
            />
          ))}

          {recipesData.items.length === 0 && (
            <p className="text-gray-500 text-sm">Рецепты не найдены.</p>
          )}

          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-500">Всего рецептов: {recipesData.total}</p>
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
                disabled={!recipesData.has_more}
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
