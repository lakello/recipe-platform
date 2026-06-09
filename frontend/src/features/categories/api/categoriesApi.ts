import { apiFetch, apiJson } from '@/shared/api/client'

export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  name: string
  description?: string
}

export interface CategoryUpdate {
  name?: string
  description?: string
}

export const categoriesApi = {
  list: () => apiJson<Category[]>('/api/categories'),

  get: (id: string) => apiJson<Category>(`/api/categories/${id}`),

  create: (data: CategoryCreate) =>
    apiJson<Category>('/api/categories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: string, data: CategoryUpdate) =>
    apiJson<Category>(`/api/categories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  remove: async (id: string) => {
    const res = await apiFetch(`/api/categories/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Не удалось удалить категорию')
  },
}
