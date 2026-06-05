import { apiJson, apiFetch } from '@/shared/api/client'
import type { Category } from '@/features/categories/api/categoriesApi'
import type { RecipeIngredientRead, RecipeStepRead } from '@/features/ingredients/api/ingredientsApi'

export type RecipeStatus = 'draft' | 'published' | 'deleted'
export type RecipeVisibility = 'public' | 'private'
export type Difficulty = 'easy' | 'medium' | 'hard'

export interface Recipe {
  id: string
  author_id: string
  title: string
  description: string | null
  status: RecipeStatus
  visibility: RecipeVisibility
  cooking_time_minutes: number | null
  servings: number | null
  difficulty: Difficulty | null
  category_id: string | null
  category: Category | null
  ingredients: RecipeIngredientRead[]
  steps: RecipeStepRead[]
  created_at: string
  updated_at: string
}

export interface RecipeCreate {
  title: string
  description?: string
  visibility: RecipeVisibility
  cooking_time_minutes?: number
  servings?: number
  difficulty?: Difficulty
  category_id?: string
}

export interface RecipeUpdate {
  title?: string
  description?: string
  status?: RecipeStatus
  visibility?: RecipeVisibility
  cooking_time_minutes?: number
  servings?: number
  difficulty?: Difficulty
  category_id?: string | null
}

export const recipesApi = {
  list: (categoryId?: string) =>
    apiJson<Recipe[]>(
      categoryId ? `/api/recipes?category_id=${categoryId}` : '/api/recipes',
    ),

  get: (id: string) => apiJson<Recipe>(`/api/recipes/${id}`),

  create: (data: RecipeCreate) =>
    apiJson<Recipe>('/api/recipes', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: string, data: RecipeUpdate) =>
    apiJson<Recipe>(`/api/recipes/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  remove: async (id: string) => {
    const res = await apiFetch(`/api/recipes/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Не удалось удалить рецепт')
  },
}
