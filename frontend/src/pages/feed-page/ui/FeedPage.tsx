import { Link, useNavigate } from 'react-router-dom'
import { useFeed } from '@/features/recipes/hooks/useRecipes'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { RecipeCard } from '@/features/recipes/ui/RecipeCard'
import { Button } from '@/shared/ui/Button'

export function FeedPage() {
  const navigate = useNavigate()
  const { data: recipes, isPending, error } = useFeed()
  const { data: user } = useCurrentUser()

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <div className="flex items-center gap-3 mb-6">
        <Button variant="secondary" onClick={() => navigate(-1)}>← Назад</Button>
        <h1 className="text-2xl font-bold text-gray-900">Лента</h1>
      </div>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {recipes && recipes.length === 0 && (
        <div className="text-center py-16">
          <p className="text-gray-500 mb-3">
            Вы ни на кого не подписаны или у авторов нет рецептов.
          </p>
          <Link to="/recipes">
            <Button variant="secondary">Все рецепты</Button>
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {recipes?.map((recipe) => (
          <RecipeCard key={recipe.id} recipe={recipe} isAuthenticated={!!user} />
        ))}
      </div>
    </div>
  )
}
