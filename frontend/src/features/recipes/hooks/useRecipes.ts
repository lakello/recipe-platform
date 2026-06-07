import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { recipesApi, type RecipeCreate, type RecipeUpdate } from '../api/recipesApi'

export const RECIPES_KEY = ['recipes']

export function useRecipesList(categoryId?: string) {
  return useQuery({
    queryKey: categoryId ? [...RECIPES_KEY, { categoryId }] : RECIPES_KEY,
    queryFn: () => recipesApi.list(categoryId),
  })
}

export function useUserRecipes(authorId: string) {
  return useQuery({
    queryKey: [...RECIPES_KEY, { authorId }],
    queryFn: () => recipesApi.listByAuthor(authorId),
  })
}

export function useRecipe(id: string) {
  return useQuery({
    queryKey: [...RECIPES_KEY, id],
    queryFn: () => recipesApi.get(id),
  })
}

export function useCreateRecipe() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: (data: RecipeCreate) => recipesApi.create(data),
    onSuccess: (recipe) => {
      queryClient.invalidateQueries({ queryKey: RECIPES_KEY })
      navigate(`/recipes/${recipe.id}`)
    },
  })
}

export function useUpdateRecipe(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: RecipeUpdate) => recipesApi.update(id, data),
    onSuccess: (recipe) => {
      queryClient.setQueryData([...RECIPES_KEY, id], recipe)
      queryClient.invalidateQueries({ queryKey: RECIPES_KEY })
    },
  })
}

export function useDeleteRecipe() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: (id: string) => recipesApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RECIPES_KEY })
      navigate('/recipes')
    },
  })
}
