import { useFavorite } from '../hooks/useLikes'

interface FavoriteButtonProps {
  recipeId: string
  isFavorited: boolean
  isAuthenticated: boolean
}

export function FavoriteButton({ recipeId, isFavorited, isAuthenticated }: FavoriteButtonProps) {
  const { addMutation, removeMutation } = useFavorite(recipeId)
  const isPending = addMutation.isPending || removeMutation.isPending

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!isAuthenticated || isPending) return
    if (isFavorited) {
      removeMutation.mutate()
    } else {
      addMutation.mutate()
    }
  }

  return (
    <button
      onClick={handleClick}
      disabled={isPending || !isAuthenticated}
      title={
        isAuthenticated
          ? isFavorited
            ? 'Убрать из избранного'
            : 'В избранное'
          : 'Войдите, чтобы добавлять в избранное'
      }
      className={`flex items-center gap-1 text-sm transition-colors px-2 py-1 rounded-md ${
        isFavorited
          ? 'text-yellow-500 hover:text-yellow-600'
          : 'text-gray-400 hover:text-yellow-400'
      } disabled:opacity-50 disabled:cursor-default`}
    >
      <span>{isFavorited ? '★' : '☆'}</span>
    </button>
  )
}
