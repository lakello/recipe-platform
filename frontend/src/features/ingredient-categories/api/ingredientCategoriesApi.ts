import { apiJson, apiFetch } from '@/shared/api/client'

export interface IngredientCategory {
  id: string
  name: string
  created_at: string
}

export const ingredientCategoriesApi = {
  list: (): Promise<IngredientCategory[]> =>
    apiJson<IngredientCategory[]>('/api/ingredient-categories'),

  create: (name: string): Promise<IngredientCategory> =>
    apiJson<IngredientCategory>('/api/ingredient-categories', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),

  update: (id: string, name: string): Promise<IngredientCategory> =>
    apiJson<IngredientCategory>(`/api/ingredient-categories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    }),

  delete: (id: string): Promise<void> =>
    apiFetch(`/api/ingredient-categories/${id}`, { method: 'DELETE' }).then(() => {}),
}
