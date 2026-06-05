import { Link, useNavigate, useParams } from 'react-router-dom'
import { useDeleteRecipe, useRecipe, useUpdateRecipe } from '@/features/recipes/hooks/useRecipes'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { Button } from '@/shared/ui/Button'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

export function RecipePage() {
  const { recipeId } = useParams<{ recipeId: string }>()
  const navigate = useNavigate()
  const { data: recipe, isPending, error } = useRecipe(recipeId!)
  const { data: user } = useCurrentUser()
  const { mutate: update, isPending: isPublishing } = useUpdateRecipe(recipeId!)
  const { mutate: remove, isPending: isDeleting } = useDeleteRecipe()

  const isAuthor = !!user && !!recipe && user.id === recipe.author_id

  if (isPending)
    return <div className="mx-auto max-w-2xl px-4 py-12 text-gray-500">Загрузка...</div>
  if (error)
    return <div className="mx-auto max-w-2xl px-4 py-12 text-red-500">{error.message}</div>
  if (!recipe) return null

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <button
        onClick={() => navigate(-1)}
        className="mb-6 text-sm text-gray-500 hover:text-gray-700"
      >
        ← Назад
      </button>

      <div className="rounded-xl bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-900">{recipe.title}</h1>
          <div className="flex flex-col gap-1 items-end shrink-0">
            {recipe.status === 'draft' ? (
              <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                Черновик
              </span>
            ) : (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                Опубликован
              </span>
            )}
            {recipe.visibility === 'private' && (
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                Приватный
              </span>
            )}
          </div>
        </div>

        {recipe.description && (
          <p className="text-gray-700 mb-6 whitespace-pre-line">{recipe.description}</p>
        )}

        <dl className="grid grid-cols-3 gap-4 text-sm mb-6">
          {recipe.cooking_time_minutes && (
            <div>
              <dt className="text-gray-500">Время</dt>
              <dd className="font-medium">{recipe.cooking_time_minutes} мин</dd>
            </div>
          )}
          {recipe.servings && (
            <div>
              <dt className="text-gray-500">Порций</dt>
              <dd className="font-medium">{recipe.servings}</dd>
            </div>
          )}
          {recipe.difficulty && (
            <div>
              <dt className="text-gray-500">Сложность</dt>
              <dd className="font-medium">{DIFFICULTY_LABELS[recipe.difficulty]}</dd>
            </div>
          )}
        </dl>

        {isAuthor && (
          <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-100">
            {recipe.status === 'draft' && (
              <Button loading={isPublishing} onClick={() => update({ status: 'published' })}>
                Опубликовать
              </Button>
            )}
            <Link to={`/recipes/${recipe.id}/edit`}>
              <Button variant="secondary">Редактировать</Button>
            </Link>
            <Button
              variant="danger"
              loading={isDeleting}
              onClick={() => {
                if (confirm('Удалить рецепт?')) remove(recipe.id)
              }}
            >
              Удалить
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
