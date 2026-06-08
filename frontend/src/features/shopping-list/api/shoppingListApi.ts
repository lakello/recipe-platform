import { apiJson, apiFetch } from '@/shared/api/client'
import type { Ingredient } from '@/features/ingredients/api/ingredientsApi'

export interface ShoppingListItem {
  id: string
  ingredient_id: string | null
  ingredient: Ingredient | null
  name: string
  amount: number | null
  unit: string | null
  is_bought: boolean
  is_manual: boolean
  created_at: string
}

export interface ShoppingList {
  id: string
  last_generated_at: string | null
  items: ShoppingListItem[]
}

export type GenerationMode = 'today' | 'week' | 'custom'

export interface GeneratePayload {
  mode: GenerationMode
  dates?: string[]
}

export interface AddItemPayload {
  ingredient_id?: string
  name: string
  amount?: number
  unit?: string
}

export const shoppingListApi = {
  getList: (): Promise<ShoppingList> => apiJson<ShoppingList>('/api/shopping-list'),

  generate: (payload: GeneratePayload): Promise<ShoppingList> =>
    apiJson<ShoppingList>('/api/shopping-list/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  addItem: (payload: AddItemPayload): Promise<ShoppingListItem> =>
    apiJson<ShoppingListItem>('/api/shopping-list/items', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateItem: (
    itemId: string,
    data: { is_bought?: boolean; amount?: number; unit?: string },
  ): Promise<ShoppingListItem> =>
    apiJson<ShoppingListItem>(`/api/shopping-list/items/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteItem: (itemId: string): Promise<void> =>
    apiFetch(`/api/shopping-list/items/${itemId}`, { method: 'DELETE' }).then(() => {}),
}
