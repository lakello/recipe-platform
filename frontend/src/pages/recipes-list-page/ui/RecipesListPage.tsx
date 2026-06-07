import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCategoriesList } from '@/features/categories/hooks/useCategories'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { useRecipesList } from '@/features/recipes/hooks/useRecipes'
import { RecipeCard } from '@/features/recipes/ui/RecipeCard'
import { Button } from '@/shared/ui/Button'

export function RecipesListPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()
  const { data: recipes, isPending, error } = useRecipesList(selectedCategory)
  const { data: user } = useCurrentUser()
  const { data: categories } = useCategoriesList()

  const published = recipes?.filter((r) => r.status === 'published') ?? []

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      {/* Шапка */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Рецепты</h1>
        <div className="flex gap-2 flex-wrap justify-end">
          {user ? (
            <>
              {(user.role === 'admin' || user.role === 'superadmin') && (
                <Link to="/admin/categories">
                  <Button variant="secondary">Категории</Button>
                </Link>
              )}
              <Link to="/feed">
                <Button variant="secondary">Лента</Button>
              </Link>
              <Link to="/favorites">
                <Button variant="secondary">Избранное</Button>
              </Link>
              <Link to="/recipes/drafts">
                <Button variant="secondary">Черновики</Button>
              </Link>
              <Link to="/recipes/new">
                <Button>Создать рецепт</Button>
              </Link>
              <Link to="/profile">
                <Button variant="secondary">Профиль</Button>
              </Link>
            </>
          ) : (
            <Link to="/login">
              <Button>Войти</Button>
            </Link>
          )}
        </div>
      </div>

      {/* Фильтр по категориям */}
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
      {!isPending && published.length === 0 && (
        <p className="text-gray-500">Рецептов пока нет. Будьте первым!</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {published.map((recipe) => (
          <RecipeCard key={recipe.id} recipe={recipe} isAuthenticated={!!user} />
        ))}
      </div>
    </div>
  )
}
