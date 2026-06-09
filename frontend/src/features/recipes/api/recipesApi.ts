import { apiJson, apiFetch } from '@/shared/api/client'
import type { Category } from '@/features/categories/api/categoriesApi'
import type { RecipeIngredientRead, RecipeStepRead } from '@/features/ingredients/api/ingredientsApi'

export type RecipeStatus = 'draft' | 'published' | 'deleted'
export type RecipeVisibility = 'public' | 'private'
export type Difficulty = 'easy' | 'medium' | 'hard'

export interface RecipeAuthor {
  id: string
  username: string
  role: string
  avatar_url: string | null
}

export interface Recipe {
  id: string
  author_id: string
  author: RecipeAuthor
  title: string
  description: string | null
  status: RecipeStatus
  visibility: RecipeVisibility
  cooking_time_minutes: number | null
  servings: number | null
  difficulty: Difficulty | null
  category_id: string | null
  category: Category | null
  photo: { id: string; key: string; content_type: string; created_at: string } | null
  ingredients: RecipeIngredientRead[]
  steps: RecipeStepRead[]
  likes_count: number
  is_liked: boolean
  is_favorited: boolean
  comment_count: number
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

  listByAuthor: (authorId: string) =>
    apiJson<Recipe[]>(`/api/recipes?author_id=${authorId}`),

  getFeed: (page = 1, size = 20) =>
    apiJson<Recipe[]>(`/api/feed?page=${page}&size=${size}`),

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
