import type { UserProfile } from '@/features/profile/api/profileApi'
import { useComments, useAddComment } from '../hooks/useComments'
import { CommentItem } from './CommentItem'
import { CommentForm } from './CommentForm'

interface CommentListProps {
  recipeId: string
  currentUser: UserProfile | undefined
}

export function CommentList({ recipeId, currentUser }: CommentListProps) {
  const { data, isPending, error } = useComments(recipeId)
  const addComment = useAddComment(recipeId)

  const handleAdd = (body: string) => {
    addComment.mutate({ body })
  }

  return (
    <div id="comments" className="rounded-xl bg-white p-6 shadow-sm flex flex-col gap-4">
      <h2 className="text-lg font-semibold text-gray-900">Комментарии</h2>

      {currentUser ? (
        <CommentForm onSubmit={handleAdd} isPending={addComment.isPending} />
      ) : (
        <p className="text-sm text-gray-400">Войдите, чтобы оставить комментарий.</p>
      )}

      {isPending && <p className="text-sm text-gray-400">Загрузка...</p>}
      {error && <p className="text-sm text-red-500">{error.message}</p>}

      {data && data.items.length === 0 && (
        <p className="text-sm text-gray-400">Комментариев пока нет. Будьте первым!</p>
      )}

      {data && data.items.length > 0 && (
        <div className="flex flex-col gap-3">
          {data.items.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              recipeId={recipeId}
              currentUser={currentUser}
            />
          ))}
        </div>
      )}

      {data?.has_more && (
        <p className="text-xs text-gray-400 text-center">
          Показано {data.items.length} из {data.total} комментариев
        </p>
      )}
    </div>
  )
}
