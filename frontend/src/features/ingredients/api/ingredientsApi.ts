import { apiJson } from '@/shared/api/client'

export type IngredientUnit =
  | 'g' | 'kg' | 'ml' | 'l' | 'tsp' | 'tbsp' | 'pcs' | 'cup' | 'pinch' | 'to_taste'

export const UNIT_LABELS: Record<IngredientUnit, string> = {
  g: 'г',
  kg: 'кг',
  ml: 'мл',
  l: 'л',
  tsp: 'ч.л.',
  tbsp: 'ст.л.',
  pcs: 'шт',
  cup: 'стакан',
  pinch: 'щепотка',
  to_taste: 'по вкусу',
}

export interface Ingredient {
  id: string
  name: string
  created_at: string
}

export interface RecipeIngredientRead {
  id: string
  ingredient_id: string
  ingredient: Ingredient
  amount: number | null
  unit: IngredientUnit | null
  order: number
}

export interface RecipeIngredientItem {
  ingredient_name: string
  amount?: number
  unit?: IngredientUnit
}

export interface RecipeStepRead {
  id: string
  order: number
  title: string | null
  description: string
}

export interface RecipeStepItem {
  title?: string
  description: string
}

export const ingredientsApi = {
  search: (query: string) =>
    apiJson<Ingredient[]>(`/api/ingredients?search=${encodeURIComponent(query)}`),

  setRecipeIngredients: (recipeId: string, items: RecipeIngredientItem[]) =>
    apiJson(`/api/recipes/${recipeId}/ingredients`, {
      method: 'PUT',
      body: JSON.stringify(items),
    }),

  setRecipeSteps: (recipeId: string, items: RecipeStepItem[]) =>
    apiJson(`/api/recipes/${recipeId}/steps`, {
      method: 'PUT',
      body: JSON.stringify(items),
    }),
}
