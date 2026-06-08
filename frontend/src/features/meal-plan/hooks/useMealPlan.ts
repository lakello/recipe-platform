import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { mealPlanApi, type AddItemPayload } from '../api/mealPlanApi'

const KEY = (weekStart: string) => ['meal-plan', weekStart]

export function useWeekPlan(weekStart: string) {
  return useQuery({
    queryKey: KEY(weekStart),
    queryFn: () => mealPlanApi.getWeek(weekStart),
  })
}

export function useAddMealPlanItem(weekStart: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: AddItemPayload) => mealPlanApi.addItem(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY(weekStart) }),
  })
}

export function useUpdateMealPlanItem(weekStart: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ itemId, servings }: { itemId: string; servings: number }) =>
      mealPlanApi.updateItem(itemId, servings),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY(weekStart) }),
  })
}

export function useDeleteMealPlanItem(weekStart: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (itemId: string) => mealPlanApi.deleteItem(itemId),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY(weekStart) }),
  })
}

export function useCopyToNextWeek(weekStart: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => mealPlanApi.copyToNextWeek(weekStart),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: KEY(weekStart) })
      qc.setQueryData(KEY(data.week_start), data)
    },
  })
}

export function useCopyFromWeek(targetWeekStart: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (sourceWeekStart: string) =>
      mealPlanApi.copyFromWeek(sourceWeekStart, targetWeekStart),
    onSuccess: (data) => {
      qc.setQueryData(KEY(targetWeekStart), data)
    },
  })
}
