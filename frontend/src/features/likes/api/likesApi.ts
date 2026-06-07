import { apiJson, apiFetch } from '@/shared/api/client'
import type { Recipe } from '@/features/recipes/api/recipesApi'

export interface LikeStatus {
  likes_count: number
  is_liked: boolean
}

export interface FavoriteStatus {
  is_favorited: boolean
}

export const likesApi = {
  like: (recipeId: string) =>
    apiJson<LikeStatus>(`/api/recipes/${recipeId}/like`, { method: 'POST' }),

  unlike: (recipeId: string) =>
    apiJson<LikeStatus>(`/api/recipes/${recipeId}/like`, { method: 'DELETE' }),

  addFavorite: (recipeId: string) =>
    apiJson<FavoriteStatus>(`/api/recipes/${recipeId}/favorite`, { method: 'POST' }),

  removeFavorite: async (recipeId: string) => {
    const res = await apiFetch(`/api/recipes/${recipeId}/favorite`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Не удалось удалить из избранного')
    return res.json() as Promise<FavoriteStatus>
  },

  listFavorites: () => apiJson<Recipe[]>('/api/users/me/favorites'),
}
