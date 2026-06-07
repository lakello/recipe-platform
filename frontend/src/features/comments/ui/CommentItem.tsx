import { useState } from 'react'
import type { Comment } from '../api/commentsApi'
import type { UserProfile } from '@/features/profile/api/profileApi'
import { UserLink } from '@/shared/ui/UserLink'
import { CommentForm } from './CommentForm'
import { useAddComment, useEditComment, useDeleteComment, useHideComment, useUnhideComment, useReplies } from '../hooks/useComments'

interface CommentItemProps {
  comment: Comment
  recipeId: string
  currentUser: UserProfile | undefined
  isReply?: boolean
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function CommentItem({ comment, recipeId, currentUser, isReply = false }: CommentItemProps) {
  const [showReplyForm, setShowReplyForm] = useState(false)
  const [editing, setEditing] = useState(false)
  const [showReplies, setShowReplies] = useState(false)

  const isModerator = currentUser?.role === 'admin' || currentUser?.role === 'superadmin'
  const isOwner = currentUser?.id === comment.author_id
  const isGhost = comment.is_deleted || comment.is_hidden

  const addComment = useAddComment(recipeId)
  const editComment = useEditComment(recipeId)
  const deleteComment = useDeleteComment(recipeId)
  const hideComment = useHideComment(recipeId)
  const unhideComment = useUnhideComment(recipeId)

  const { data: repliesPage } = useReplies(comment.id, showReplies && !isReply)

  const handleReply = (body: string) => {
    addComment.mutate(
      { body, parentId: comment.id },
      { onSuccess: () => { setShowReplyForm(false); setShowReplies(true) } },
    )
  }

  const handleEdit = (body: string) => {
    editComment.mutate({ commentId: comment.id, body }, { onSuccess: () => setEditing(false) })
  }

  const handleDelete = () => {
    if (confirm('Удалить комментарий?')) {
      deleteComment.mutate(comment.id)
    }
  }

  return (
    <div className={`flex flex-col gap-1 ${isReply ? 'ml-8 pl-4 border-l-2 border-gray-100' : ''}`}>
      <div className="rounded-lg bg-white border border-gray-100 p-3">
        <div className="flex items-center justify-between mb-1">
          <UserLink
            userId={comment.author.id}
            username={comment.author.username}
            avatarUrl={comment.author.avatar_url}
          />
          <span className="text-xs text-gray-400">{formatDate(comment.created_at)}</span>
        </div>

        {editing ? (
          <CommentForm
            defaultValue={comment.body}
            onSubmit={handleEdit}
            onCancel={() => setEditing(false)}
            isPending={editComment.isPending}
            submitLabel="Сохранить"
          />
        ) : (
          <p className={`text-sm whitespace-pre-line ${isGhost ? 'text-gray-400 italic' : 'text-gray-700'}`}>
            {comment.body}
          </p>
        )}

        {!editing && (
          <div className="flex gap-3 mt-2 flex-wrap">
            {!isReply && !isGhost && currentUser && (
              <button
                className="text-xs text-gray-400 hover:text-blue-500"
                onClick={() => setShowReplyForm((v) => !v)}
              >
                Ответить
              </button>
            )}
            {isOwner && !comment.is_deleted && !editing && (
              <>
                <button
                  className="text-xs text-gray-400 hover:text-blue-500"
                  onClick={() => setEditing(true)}
                >
                  Изменить
                </button>
                <button
                  className="text-xs text-gray-400 hover:text-red-500"
                  onClick={handleDelete}
                >
                  Удалить
                </button>
              </>
            )}
            {isModerator && !comment.is_deleted && (
              comment.is_hidden ? (
                <button
                  className="text-xs text-orange-400 hover:text-orange-600"
                  onClick={() => unhideComment.mutate(comment.id)}
                >
                  Показать
                </button>
              ) : (
                <button
                  className="text-xs text-orange-400 hover:text-orange-600"
                  onClick={() => hideComment.mutate(comment.id)}
                >
                  Скрыть
                </button>
              )
            )}
          </div>
        )}
      </div>

      {showReplyForm && (
        <div className="ml-8 pl-4 border-l-2 border-blue-100">
          <CommentForm
            onSubmit={handleReply}
            onCancel={() => setShowReplyForm(false)}
            isPending={addComment.isPending}
            placeholder="Напишите ответ..."
            submitLabel="Ответить"
          />
        </div>
      )}

      {!isReply && comment.reply_count > 0 && (
        <button
          className="ml-8 text-xs text-blue-500 hover:text-blue-700 text-left"
          onClick={() => setShowReplies((v) => !v)}
        >
          {showReplies
            ? 'Скрыть ответы'
            : `Показать ответы (${comment.reply_count})`}
        </button>
      )}

      {showReplies && repliesPage && (
        <div className="flex flex-col gap-2">
          {repliesPage.items.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              recipeId={recipeId}
              currentUser={currentUser}
              isReply
            />
          ))}
        </div>
      )}
    </div>
  )
}
