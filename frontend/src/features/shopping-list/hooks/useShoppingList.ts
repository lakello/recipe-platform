import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  shoppingListApi,
  type AddItemPayload,
  type GeneratePayload,
} from '../api/shoppingListApi'

const KEY = ['shopping-list']

export function useShoppingList() {
  return useQuery({ queryKey: KEY, queryFn: shoppingListApi.getList })
}

export function useGenerateShoppingList() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: GeneratePayload) => shoppingListApi.generate(payload),
    onSuccess: (data) => qc.setQueryData(KEY, data),
  })
}

export function useAddShoppingListItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: AddItemPayload) => shoppingListApi.addItem(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}

export function useToggleBought() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ itemId, is_bought }: { itemId: string; is_bought: boolean }) =>
      shoppingListApi.updateItem(itemId, { is_bought }),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}

export function useDeleteShoppingListItem() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (itemId: string) => shoppingListApi.deleteItem(itemId),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}
