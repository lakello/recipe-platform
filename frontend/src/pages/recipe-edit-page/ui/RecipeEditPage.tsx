import { useNavigate, useParams } from 'react-router-dom'
import { useRecipe, useUpdateRecipe } from '@/features/recipes/hooks/useRecipes'
import { RecipeForm, type RecipeFormData } from '@/features/recipes/ui/RecipeForm'

export function RecipeEditPage() {
  const { recipeId } = useParams<{ recipeId: string }>()
  const navigate = useNavigate()
  const { data: recipe, isPending: isLoading } = useRecipe(recipeId!)
  const { mutate: update, isPending, error } = useUpdateRecipe(recipeId!)

  if (isLoading)
    return <div className="mx-auto max-w-2xl px-4 py-12 text-gray-500">Загрузка...</div>
  if (!recipe) return null

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Редактировать рецепт</h1>
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <RecipeForm
          defaultValues={recipe}
          onSubmit={(data: RecipeFormData) => {
            update(data, { onSuccess: () => navigate(`/recipes/${recipeId}`, { replace: true }) })
          }}
          isPending={isPending}
          error={error}
          submitLabel="Сохранить"
        />
      </div>
    </div>
  )
}
