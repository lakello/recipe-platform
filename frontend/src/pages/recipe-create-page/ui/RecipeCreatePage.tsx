import { useCreateRecipe } from '@/features/recipes/hooks/useRecipes'
import { RecipeForm, type RecipeFormData } from '@/features/recipes/ui/RecipeForm'

export function RecipeCreatePage() {
  const { mutate: create, isPending, error } = useCreateRecipe()

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Новый рецепт</h1>
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <RecipeForm
          onSubmit={(data: RecipeFormData) => create(data)}
          isPending={isPending}
          error={error}
          submitLabel="Создать"
        />
      </div>
    </div>
  )
}
