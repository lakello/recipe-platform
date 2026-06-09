import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../api/adminApi'
import { apiJson } from '@/shared/api/client'
import type { UserRole } from '@/features/profile/api/profileApi'

export const ADMIN_USERS_KEY = (page: number, search?: string, role?: string) =>
  ['admin', 'users', page, search, role] as const
export const ADMIN_REPORTS_KEY = (page: number, status?: string) =>
  ['admin', 'reports', page, status] as const
export const ADMIN_RECIPES_KEY = (page: number, search?: string, hasComments?: boolean) =>
  ['admin', 'recipes', page, search, hasComments] as const
export const ADMIN_COMMENTS_KEY = (recipeId?: string, search?: string, status?: string) =>
  ['admin', 'comments', recipeId, search, status] as const

export function useAdminUsers(page = 1, search?: string, role?: string) {
  return useQuery({
    queryKey: ADMIN_USERS_KEY(page, search, role),
    queryFn: () => adminApi.getUsers(page, 20, search, role),
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

export function useAdminRecipes(page = 1, search?: string, hasComments?: boolean) {
  return useQuery({
    queryKey: ADMIN_RECIPES_KEY(page, search, hasComments),
    queryFn: () => adminApi.getAdminRecipes(page, 20, search, hasComments),
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

export function useAdminComments(
  recipeId?: string,
  search?: string,
  status?: string,
  enabled = true,
) {
  return useQuery({
    queryKey: ADMIN_COMMENTS_KEY(recipeId, search, status),
    queryFn: () => adminApi.getAdminComments({ recipeId, search, status }),
    enabled,
  })
}

export function useDeleteCommentAdmin() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (commentId: string) => adminApi.deleteCommentAdmin(commentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'comments'] }),
  })
}

export function useHideCommentAdmin() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (commentId: string) =>
      apiJson(`/api/comments/${commentId}/hide`, { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'comments'] }),
  })
}

export function useUnhideCommentAdmin() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (commentId: string) =>
      apiJson(`/api/comments/${commentId}/unhide`, { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'comments'] }),
  })
}
