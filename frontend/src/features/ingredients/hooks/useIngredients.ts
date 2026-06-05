import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { RECIPES_KEY } from '@/features/recipes/hooks/useRecipes'
import {
  ingredientsApi,
  type RecipeIngredientItem,
  type RecipeStepItem,
} from '../api/ingredientsApi'

export function useIngredientSearch(query: string) {
  return useQuery({
    queryKey: ['ingredients', 'search', query],
    queryFn: () => ingredientsApi.search(query),
    enabled: query.length >= 1,
  })
}

export function useSetRecipeIngredients(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (items: RecipeIngredientItem[]) =>
      ingredientsApi.setRecipeIngredients(recipeId, items),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: [...RECIPES_KEY, recipeId] }),
  })
}

export function useSetRecipeSteps(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (items: RecipeStepItem[]) =>
      ingredientsApi.setRecipeSteps(recipeId, items),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: [...RECIPES_KEY, recipeId] }),
  })
}
