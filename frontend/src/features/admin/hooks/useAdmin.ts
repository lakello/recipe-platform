import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../api/adminApi'
import type { UserRole } from '@/features/profile/api/profileApi'

export const ADMIN_USERS_KEY = (page: number) => ['admin', 'users', page] as const
export const ADMIN_REPORTS_KEY = (page: number, status?: string) =>
  ['admin', 'reports', page, status] as const
export const ADMIN_RECIPES_KEY = (page: number) => ['admin', 'recipes', page] as const
export const ADMIN_COMMENTS_KEY = (page: number) => ['admin', 'comments', page] as const
export const ADMIN_AUDIT_KEY = (page: number) => ['admin', 'audit', page] as const

export function useAdminUsers(page = 1) {
  return useQuery({
    queryKey: ADMIN_USERS_KEY(page),
    queryFn: () => adminApi.getUsers(page),
  })
}

export function useAssignRole() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
      adminApi.assignRole(userId, role),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'users'] }),
  })
}

export function useBlockUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ userId, reason }: { userId: string; reason?: string }) =>
      adminApi.blockUser(userId, reason),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'users'] }),
  })
}

export function useUnblockUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (userId: string) => adminApi.unblockUser(userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'users'] }),
  })
}

export function useAdminReports(page = 1, status?: string) {
  return useQuery({
    queryKey: ADMIN_REPORTS_KEY(page, status),
    queryFn: () => adminApi.getReports(page, 20, status),
  })
}

export function useReviewReport() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (reportId: string) => adminApi.reviewReport(reportId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'reports'] }),
  })
}

export function useDismissReport() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (reportId: string) => adminApi.dismissReport(reportId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'reports'] }),
  })
}

export function useAdminRecipes(page = 1) {
  return useQuery({
    queryKey: ADMIN_RECIPES_KEY(page),
    queryFn: () => adminApi.getAdminRecipes(page),
  })
}

export function useHideRecipe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ recipeId, reason }: { recipeId: string; reason?: string }) =>
      adminApi.hideRecipe(recipeId, reason),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'recipes'] }),
  })
}

export function useUnhideRecipe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (recipeId: string) => adminApi.unhideRecipe(recipeId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'recipes'] }),
  })
}

export function useAdminComments(page = 1) {
  return useQuery({
    queryKey: ADMIN_COMMENTS_KEY(page),
    queryFn: () => adminApi.getAdminComments(page),
  })
}

export function useAuditLog(page = 1) {
  return useQuery({
    queryKey: ADMIN_AUDIT_KEY(page),
    queryFn: () => adminApi.getAuditLog(page),
  })
}
