import { useLike } from '../hooks/useLikes'

interface LikeButtonProps {
  recipeId: string
  likesCount: number
  isLiked: boolean
  isAuthenticated: boolean
}

export function LikeButton({ recipeId, likesCount, isLiked, isAuthenticated }: LikeButtonProps) {
  const { likeMutation, unlikeMutation } = useLike(recipeId)
  const isPending = likeMutation.isPending || unlikeMutation.isPending

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!isAuthenticated || isPending) return
    if (isLiked) {
      unlikeMutation.mutate()
    } else {
      likeMutation.mutate()
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={isPending || !isAuthenticated}
      title={isAuthenticated ? (isLiked ? 'Убрать лайк' : 'Поставить лайк') : 'Войдите, чтобы лайкать'}
      className={`flex items-center gap-1 text-sm transition-colors px-2 py-1 rounded-md ${
        isLiked
          ? 'text-red-500 hover:text-red-600'
          : 'text-gray-400 hover:text-red-400'
      } disabled:opacity-50 disabled:cursor-default`}
    >
      <span>{isLiked ? '❤️' : '🤍'}</span>
      <span>{likesCount}</span>
    </button>
  )
}
