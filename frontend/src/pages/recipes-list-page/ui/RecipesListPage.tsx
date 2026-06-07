import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCategoriesList } from '@/features/categories/hooks/useCategories'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { useRecipesList } from '@/features/recipes/hooks/useRecipes'
import { LikeButton } from '@/features/likes/ui/LikeButton'
import { FavoriteButton } from '@/features/likes/ui/FavoriteButton'
import { Button } from '@/shared/ui/Button'
import type { Recipe } from '@/features/recipes/api/recipesApi'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

function VisibilityBadge({ visibility }: { visibility: Recipe['visibility'] }) {
  if (visibility === 'private')
    return (
      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
        Приватный
      </span>
    )
  return null
}

export function RecipesListPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()
  const { data: recipes, isPending, error } = useRecipesList(selectedCategory)
  const { data: user } = useCurrentUser()
  const { data: categories } = useCategoriesList()

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Рецепты</h1>
        <div className="flex gap-2">
          {user && (
            <>
              {user.role === 'admin' || user.role === 'superadmin' ? (
                <Link to="/admin/categories">
                  <Button variant="secondary">Категории</Button>
                </Link>
              ) : null}
              <Link to="/favorites">
                <Button variant="secondary">Избранное</Button>
              </Link>
              <Link to="/recipes/drafts">
                <Button variant="secondary">Черновики</Button>
              </Link>
              <Link to="/recipes/new">
                <Button>Создать рецепт</Button>
              </Link>
            </>
          )}
          <Link to="/profile">
            <Button variant="secondary">Профиль</Button>
          </Link>
        </div>
      </div>

      {categories && categories.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          <button
            onClick={() => setSelectedCategory(undefined)}
            className={`px-3 py-1 rounded-full text-sm transition-colors ${
              !selectedCategory
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Все
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedCategory(c.id === selectedCategory ? undefined : c.id)}
              className={`px-3 py-1 rounded-full text-sm transition-colors ${
                selectedCategory === c.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>
      )}

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {recipes && recipes.filter((r) => r.status === 'published').length === 0 && (
        <p className="text-gray-500">Рецептов пока нет. Будьте первым!</p>
      )}

      <ul className="flex flex-col gap-4">
        {recipes?.filter((r) => r.status === 'published').map((recipe) => (
          <li key={recipe.id}>
            <Link
              to={`/recipes/${recipe.id}`}
              className="block rounded-xl bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h2 className="font-semibold text-gray-900 truncate">{recipe.title}</h2>
                  {recipe.category && (
                    <span className="text-xs text-blue-600 font-medium">{recipe.category.name}</span>
                  )}
                  {recipe.description && (
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">{recipe.description}</p>
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
                <div className="flex flex-col gap-1 items-end shrink-0">
                  <VisibilityBadge visibility={recipe.visibility} />
                  <div className="flex items-center gap-1">
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
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
