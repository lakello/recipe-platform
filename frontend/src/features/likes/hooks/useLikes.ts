import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { likesApi } from '../api/likesApi'
import { RECIPES_KEY } from '@/features/recipes/hooks/useRecipes'

export const FAVORITES_KEY = ['favorites']

export function useLike(recipeId: string) {
  const queryClient = useQueryClient()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: [...RECIPES_KEY, recipeId] })
    queryClient.invalidateQueries({ queryKey: RECIPES_KEY })
    queryClient.invalidateQueries({ queryKey: FAVORITES_KEY })
  }

  const likeMutation = useMutation({
    mutationFn: () => likesApi.like(recipeId),
    onSuccess: invalidate,
  })

  const unlikeMutation = useMutation({
    mutationFn: () => likesApi.unlike(recipeId),
    onSuccess: invalidate,
  })

  return { likeMutation, unlikeMutation }
}

export function useFavorite(recipeId: string) {
  const queryClient = useQueryClient()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: [...RECIPES_KEY, recipeId] })
    queryClient.invalidateQueries({ queryKey: RECIPES_KEY })
    queryClient.invalidateQueries({ queryKey: FAVORITES_KEY })
  }

  const addMutation = useMutation({
    mutationFn: () => likesApi.addFavorite(recipeId),
    onSuccess: invalidate,
  })

  const removeMutation = useMutation({
    mutationFn: () => likesApi.removeFavorite(recipeId),
    onSuccess: invalidate,
  })

  return { addMutation, removeMutation }
}

export function useFavorites() {
  return useQuery({
    queryKey: FAVORITES_KEY,
    queryFn: likesApi.listFavorites,
  })
}
