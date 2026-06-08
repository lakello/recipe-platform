import { apiJson } from '@/shared/api/client'
import type { Recipe, Difficulty } from '@/features/recipes/api/recipesApi'

export interface SearchParams {
  q?: string
  categoryId?: string
  minTime?: number
  maxTime?: number
  difficulty?: Difficulty
  includeIngredients?: string[]
  excludeIngredients?: string[]
  sort?: 'relevance' | 'newest' | 'popular'
  page?: number
  size?: number
}

export interface SearchResult {
  total: number
  page: number
  size: number
  items: Recipe[]
}

export const searchApi = {
  searchRecipes: (params: SearchParams): Promise<SearchResult> => {
    const qs = new URLSearchParams()

    if (params.q) qs.set('q', params.q)
    if (params.categoryId) qs.set('category_id', params.categoryId)
    if (params.minTime) qs.set('min_time', String(params.minTime))
    if (params.maxTime) qs.set('max_time', String(params.maxTime))
    if (params.difficulty) qs.set('difficulty', params.difficulty)
    if (params.sort) qs.set('sort', params.sort)
    if (params.page) qs.set('page', String(params.page))
    if (params.size) qs.set('size', String(params.size))
    params.includeIngredients?.forEach((i) => qs.append('include_ingredients', i))
    params.excludeIngredients?.forEach((i) => qs.append('exclude_ingredients', i))

    return apiJson<SearchResult>(`/api/search/recipes?${qs.toString()}`)
  },
}
