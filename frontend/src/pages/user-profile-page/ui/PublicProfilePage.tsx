import { Link, useNavigate, useParams } from 'react-router-dom'
import { usePublicProfile } from '@/features/profile/hooks/usePublicProfile'
import { useUserRecipes } from '@/features/recipes/hooks/useRecipes'
import { Button } from '@/shared/ui/Button'

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

export function PublicProfilePage() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const { data: user, isPending: userPending, error: userError } = usePublicProfile(userId!)
  const { data: recipes } = useUserRecipes(userId!)

  const published = recipes?.filter((r) => r.status === 'published') ?? []

  if (userPending) {
    return <div className="mx-auto max-w-lg px-4 py-12 text-gray-500">Загрузка...</div>
  }
  if (userError) {
    return <div className="mx-auto max-w-lg px-4 py-12 text-red-500">{userError.message}</div>
  }
  if (!user) return null

  return (
    <div className="mx-auto max-w-lg px-4 py-12">
      <div className="mb-8">
        <Button variant="secondary" onClick={() => navigate(-1)}>← Назад</Button>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm mb-6">
        <div className="flex items-center gap-4">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.username}
              className="w-16 h-16 rounded-full object-cover shrink-0"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <span className="text-2xl font-bold text-blue-600 uppercase">
                {user.username.charAt(0)}
              </span>
            </div>
          )}
          <div>
            <p className="text-xl font-semibold text-gray-900">{user.username}</p>
            <p className="text-sm text-gray-400">
              На платформе с{' '}
              {new Date(user.created_at).toLocaleDateString('ru-RU', {
                month: 'long',
                year: 'numeric',
              })}
            </p>
          </div>
        </div>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Рецепты</h2>

        {!recipes && <p className="text-gray-500 text-sm">Загрузка...</p>}
        {recipes && published.length === 0 && (
          <p className="text-gray-500 text-sm">Нет опубликованных рецептов.</p>
        )}

        <ul className="flex flex-col gap-3">
          {published.map((recipe) => (
            <li key={recipe.id}>
              <Link
                to={`/recipes/${recipe.id}`}
                className="flex items-center justify-between gap-3 rounded-lg border border-gray-100 px-4 py-3 hover:bg-gray-50 transition-colors"
              >
                <div className="min-w-0">
                  <p className="font-medium text-gray-900 truncate">{recipe.title}</p>
                  {recipe.difficulty && (
                    <p className="text-xs text-gray-400 mt-0.5">
                      {DIFFICULTY_LABELS[recipe.difficulty]}
                      {recipe.cooking_time_minutes && ` · ${recipe.cooking_time_minutes} мин`}
                    </p>
                  )}
                </div>
                {recipe.category && (
                  <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full shrink-0">
                    {recipe.category.name}
                  </span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
