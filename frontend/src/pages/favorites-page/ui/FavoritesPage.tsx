import { Link } from 'react-router-dom'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { useFavorites } from '@/features/likes/hooks/useLikes'
import { LikeButton } from '@/features/likes/ui/LikeButton'
import { FavoriteButton } from '@/features/likes/ui/FavoriteButton'
import { uploadsApi } from '@/features/uploads/api/uploadsApi'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

export function FavoritesPage() {
  const { data: user } = useCurrentUser()
  const { data: recipes, isPending, error } = useFavorites()

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Избранное</h1>
        <Link to="/recipes" className="text-sm text-blue-600 hover:text-blue-700">
          ← Все рецепты
        </Link>
      </div>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {recipes && recipes.length === 0 && (
        <p className="text-gray-500">Избранных рецептов пока нет.</p>
      )}

      <ul className="flex flex-col gap-4">
        {recipes?.map((recipe) => (
          <li key={recipe.id}>
            <Link
              to={`/recipes/${recipe.id}`}
              className="block rounded-xl bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4">
                {recipe.photo && (
                  <img
                    src={uploadsApi.getViewUrl(recipe.photo.key)}
                    alt={recipe.title}
                    className="w-20 h-20 object-cover rounded-lg shrink-0"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h2 className="font-semibold text-gray-900 truncate">{recipe.title}</h2>
                      {recipe.category && (
                        <span className="text-xs text-blue-600 font-medium">
                          {recipe.category.name}
                        </span>
                      )}
                      {recipe.description && (
                        <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                          {recipe.description}
                        </p>
                      )}
                      <div className="mt-2 flex flex-wrap gap-1.5 text-xs text-gray-400">
                        {recipe.cooking_time_minutes && (
                          <span>{recipe.cooking_time_minutes} мин</span>
                        )}
                        {recipe.servings && <span>· {recipe.servings} порц.</span>}
                        {recipe.difficulty && (
                          <span>· {DIFFICULTY_LABELS[recipe.difficulty]}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <LikeButton
                        recipeId={recipe.id}
                        likesCount={recipe.likes_count}
                        isLiked={recipe.is_liked}
                        isAuthenticated={!!user}
                      />
                      <FavoriteButton
                        recipeId={recipe.id}
                        isFavorited={recipe.is_favorited}
                        isAuthenticated={!!user}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
