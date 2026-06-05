import { Link } from 'react-router-dom'
import { useRecipesList } from '@/features/recipes/hooks/useRecipes'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { Button } from '@/shared/ui/Button'
import type { Recipe } from '@/features/recipes/api/recipesApi'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

function StatusBadge({ status }: { status: Recipe['status'] }) {
  if (status === 'published')
    return (
      <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
        Опубликован
      </span>
    )
  if (status === 'draft')
    return (
      <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
        Черновик
      </span>
    )
  return null
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
  const { data: recipes, isPending, error } = useRecipesList()
  const { data: user } = useCurrentUser()

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Рецепты</h1>
        <div className="flex gap-2">
          {user && (
            <>
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

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {recipes && recipes.length === 0 && (
        <p className="text-gray-500">Рецептов пока нет. Будьте первым!</p>
      )}

      <ul className="flex flex-col gap-4">
        {recipes?.map((recipe) => (
          <li key={recipe.id}>
            <Link
              to={`/recipes/${recipe.id}`}
              className="block rounded-xl bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h2 className="font-semibold text-gray-900 truncate">{recipe.title}</h2>
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
                  <StatusBadge status={recipe.status} />
                  <VisibilityBadge visibility={recipe.visibility} />
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
