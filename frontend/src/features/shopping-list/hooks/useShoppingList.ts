import { useEffect, useState } from 'react'
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
  const [taskId, setTaskId] = useState<string | null>(null)
  const [pollError, setPollError] = useState<string | null>(null)

  const statusQuery = useQuery({
    queryKey: ['shopping-list-task', taskId],
    queryFn: () => shoppingListApi.getGenerateStatus(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const s = query.state.data?.status
      if (s === 'success' || s === 'failure') return false
      return 2000
    },
  })

  useEffect(() => {
    if (!statusQuery.data) return
    const { status, error: taskError } = statusQuery.data
    if (status !== 'success' && status !== 'failure') return
    const timer = setTimeout(() => {
      if (status === 'success') {
        void qc.invalidateQueries({ queryKey: KEY })
        setTaskId(null)
      } else {
        setPollError(taskError ?? 'Ошибка генерации')
        setTaskId(null)
      }
    }, 0)
    return () => clearTimeout(timer)
  }, [statusQuery.data, qc])

  const { mutate, isPending, error } = useMutation({
    mutationFn: (payload: GeneratePayload) => shoppingListApi.generate(payload),
    onSuccess: ({ task_id }) => {
      setTaskId(task_id)
      setPollError(null)
    },
  })

  return {
    mutate,
    isPending,
    isPolling: !!taskId,
    pollError,
    mutationError: error,
  }
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
