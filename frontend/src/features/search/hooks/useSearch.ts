import { useQuery } from '@tanstack/react-query'
import { searchApi, type SearchParams } from '../api/searchApi'

export const SEARCH_KEY = ['search']

export function useSearch(params: SearchParams, enabled: boolean) {
  return useQuery({
    queryKey: [...SEARCH_KEY, params],
    queryFn: () => searchApi.searchRecipes(params),
    enabled,
  })
}
