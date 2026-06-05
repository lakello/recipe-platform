import { Link } from 'react-router-dom'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { useRecipesList } from '@/features/recipes/hooks/useRecipes'
import { Button } from '@/shared/ui/Button'

export function DraftsPage() {
  const { data: user } = useCurrentUser()
  const { data: recipes, isPending, error } = useRecipesList()

  const drafts = recipes?.filter(
    (r) => r.status === 'draft' && r.author_id === user?.id,
  )

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <div className="flex items-center gap-3 mb-8">
        <Link to="/recipes">
          <Button variant="secondary">← Рецепты</Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Мои черновики</h1>
      </div>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {drafts && drafts.length === 0 && (
        <p className="text-gray-500">Черновиков нет.</p>
      )}

      <ul className="flex flex-col gap-4">
        {drafts?.map((recipe) => (
          <li key={recipe.id}>
            <Link
              to={`/recipes/${recipe.id}`}
              className="block rounded-xl bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h2 className="font-semibold text-gray-900 truncate">{recipe.title}</h2>
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
                  </div>
                </div>
                <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full shrink-0">
                  Черновик
                </span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
