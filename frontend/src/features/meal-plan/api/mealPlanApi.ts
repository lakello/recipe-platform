import { apiJson, apiFetch } from '@/shared/api/client'
import type { Difficulty } from '@/features/recipes/api/recipesApi'
import type { Category } from '@/features/categories/api/categoriesApi'

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

export interface RecipePhoto {
  id: string
  key: string
  content_type: string
  created_at: string
}

export interface RecipeSummary {
  id: string
  title: string
  cooking_time_minutes: number | null
  servings: number | null
  difficulty: Difficulty | null
  photo: RecipePhoto | null
  category: Category | null
}

export interface MealPlanItem {
  id: string
  day_of_week: number
  meal_type: MealType
  recipe_id: string
  recipe: RecipeSummary
  servings: number
}

export interface MealPlan {
  week_start: string
  items: MealPlanItem[]
}

export interface AddItemPayload {
  week_start: string
  day_of_week: number
  meal_type: MealType
  recipe_id: string
  servings: number
}

export const mealPlanApi = {
  getWeek: (weekStart: string): Promise<MealPlan> =>
    apiJson<MealPlan>(`/api/meal-plans/week?week_start=${weekStart}`),

  addItem: (payload: AddItemPayload): Promise<MealPlanItem> =>
    apiJson<MealPlanItem>('/api/meal-plans/items', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateItem: (itemId: string, servings: number): Promise<MealPlanItem> =>
    apiJson<MealPlanItem>(`/api/meal-plans/items/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify({ servings }),
    }),

  deleteItem: (itemId: string): Promise<void> =>
    apiFetch(`/api/meal-plans/items/${itemId}`, { method: 'DELETE' }).then(() => {}),

  copyToNextWeek: (weekStart: string): Promise<MealPlan> =>
    apiJson<MealPlan>('/api/meal-plans/copy-next-week', {
      method: 'POST',
      body: JSON.stringify({ week_start: weekStart }),
    }),
}
