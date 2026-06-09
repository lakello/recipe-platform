import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ingredientCategoriesApi } from '../api/ingredientCategoriesApi'

const KEY = ['ingredient-categories']

export function useIngredientCategoriesList() {
  return useQuery({ queryKey: KEY, queryFn: ingredientCategoriesApi.list })
}

export function useCreateIngredientCategory() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => ingredientCategoriesApi.create(name),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}

export function useUpdateIngredientCategory(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => ingredientCategoriesApi.update(id, name),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}

export function useDeleteIngredientCategory() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => ingredientCategoriesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}
