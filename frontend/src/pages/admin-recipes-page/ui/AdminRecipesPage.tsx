import { useState } from 'react'
import { AdminLayout } from '@/widgets/admin-layout'
import { useAdminRecipes, useHideRecipe, useUnhideRecipe } from '@/features/admin/hooks/useAdmin'
import type { AdminRecipe } from '@/features/admin/api/adminApi'
import { Button } from '@/shared/ui/Button'

function RecipeRow({ recipe }: { recipe: AdminRecipe }) {
  const { mutate: hide, isPending: isHiding } = useHideRecipe()
  const { mutate: unhide, isPending: isUnhiding } = useUnhideRecipe()

  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="py-3 pr-4">
        <p className="font-medium text-gray-900">{recipe.title}</p>
        <p className="text-xs text-gray-400">
          {recipe.status} · {recipe.visibility}
        </p>
      </td>
      <td className="py-3 pr-4">
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            recipe.is_hidden
              ? 'bg-red-100 text-red-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {recipe.is_hidden ? 'скрыт' : 'виден'}
        </span>
      </td>
      <td className="py-3 pr-4 text-xs text-gray-400">
        {new Date(recipe.created_at).toLocaleDateString('ru-RU')}
      </td>
      <td className="py-3 text-right">
        {recipe.is_hidden ? (
          <Button
            variant="secondary"
            loading={isUnhiding}
            onClick={() => unhide(recipe.id)}
          >
            Показать
          </Button>
        ) : (
          <Button
            variant="danger"
            loading={isHiding}
            onClick={() => {
              if (confirm(`Скрыть рецепт "${recipe.title}"?`)) {
                hide({ recipeId: recipe.id })
              }
            }}
          >
            Скрыть
          </Button>
        )}
      </td>
    </tr>
  )
}

export function AdminRecipesPage() {
  const [page, setPage] = useState(1)
  const { data, isPending, error } = useAdminRecipes(page)

  return (
    <AdminLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Рецепты</h1>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {data && (
        <>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Рецепт</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Дата</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="px-4">
                {data.items.map((r) => (
                  <RecipeRow key={r.id} recipe={r} />
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-500">Всего: {data.total}</p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 1}
              >
                ←
              </Button>
              <span className="text-sm text-gray-600 self-center">стр. {page}</span>
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.has_more}
              >
                →
              </Button>
            </div>
          </div>
        </>
      )}
    </AdminLayout>
  )
}
