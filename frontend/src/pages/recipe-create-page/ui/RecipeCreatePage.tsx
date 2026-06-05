import { Link } from 'react-router-dom'
import { useCreateRecipe } from '@/features/recipes/hooks/useRecipes'
import { RecipeForm, type RecipeFormData } from '@/features/recipes/ui/RecipeForm'
import { Button } from '@/shared/ui/Button'

export function RecipeCreatePage() {
  const { mutate: create, isPending, error } = useCreateRecipe()

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <div className="flex items-center gap-3 mb-8">
        <Link to="/recipes">
          <Button variant="secondary">← Назад</Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Новый рецепт</h1>
      </div>
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
