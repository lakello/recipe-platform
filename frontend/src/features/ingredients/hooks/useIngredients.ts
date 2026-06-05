import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { RECIPES_KEY } from '@/features/recipes/hooks/useRecipes'
import type { Recipe } from '@/features/recipes/api/recipesApi'
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
      ingredientsApi.setRecipeIngredients(recipeId, items) as Promise<Recipe>,
    onSuccess: (recipe) =>
      queryClient.setQueryData([...RECIPES_KEY, recipeId], recipe),
  })
}

export function useSetRecipeSteps(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (items: RecipeStepItem[]) =>
      ingredientsApi.setRecipeSteps(recipeId, items) as Promise<Recipe>,
    onSuccess: (recipe) =>
      queryClient.setQueryData([...RECIPES_KEY, recipeId], recipe),
  })
}
