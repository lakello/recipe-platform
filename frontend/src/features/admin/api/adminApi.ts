import { apiJson } from '@/shared/api/client'
import type { UserRole } from '@/features/profile/api/profileApi'

export interface AdminUser {
  id: string
  email: string
  username: string
  role: UserRole
  is_active: boolean
  is_email_verified: boolean
  avatar_url: string | null
  created_at: string
}

export interface AdminUserPage {
  items: AdminUser[]
  total: number
  page: number
  size: number
  has_more: boolean
}

export interface Report {
  id: string
  reporter_id: string
  target_type: 'recipe' | 'comment' | 'user'
  target_id: string
  reason: string
  description: string | null
  status: 'pending' | 'reviewed' | 'dismissed'
  reviewed_by: string | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
}

export interface ReportPage {
  items: Report[]
  total: number
  page: number
  size: number
  has_more: boolean
}

export interface ReportCreate {
  target_type: 'recipe' | 'comment' | 'user'
  target_id: string
  reason: 'spam' | 'offensive' | 'misinformation' | 'other'
  description?: string
}

export interface AdminRecipe {
  id: string
  title: string
  author_id: string
  status: string
  visibility: string
  is_hidden: boolean
  created_at: string
}

export interface AdminRecipePage {
  items: AdminRecipe[]
  total: number
  page: number
  size: number
  has_more: boolean
}

export interface AdminComment {
  id: string
  recipe_id: string
  author_id: string
  body: string
  is_hidden: boolean
  is_deleted: boolean
  created_at: string
}

export interface AdminCommentPage {
  items: AdminComment[]
  total: number
  page: number
  size: number
  has_more: boolean
}

export interface AuditEntry {
  id: string
  moderator_id: string
  action_type: string
  target_type: string
  target_id: string
  reason: string | null
  meta: Record<string, unknown> | null
  created_at: string
}

export interface AuditPage {
  items: AuditEntry[]
  total: number
  page: number
  size: number
  has_more: boolean
}

export const adminApi = {
  // users
  getUsers: (page = 1, size = 20) =>
    apiJson<AdminUserPage>(`/api/admin/users?page=${page}&size=${size}`),

  assignRole: (userId: string, role: UserRole) =>
    apiJson<AdminUser>(`/api/admin/users/${userId}/role`, {
      method: 'POST',
      body: JSON.stringify({ role }),
    }),

  blockUser: (userId: string, reason?: string) =>
    apiJson<AdminUser>(`/api/admin/users/${userId}/block`, {
      method: 'POST',
      body: JSON.stringify({ reason: reason ?? null }),
    }),

  unblockUser: (userId: string) =>
    apiJson<AdminUser>(`/api/admin/users/${userId}/unblock`, {
      method: 'POST',
      body: JSON.stringify({}),
    }),

  // reports
  createReport: (data: ReportCreate) =>
    apiJson<Report>('/api/admin/reports', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getReports: (page = 1, size = 20, status?: string) => {
    const params = new URLSearchParams({ page: String(page), size: String(size) })
    if (status) params.set('status', status)
    return apiJson<ReportPage>(`/api/admin/reports?${params}`)
  },

  reviewReport: (reportId: string) =>
    apiJson<Report>(`/api/admin/reports/${reportId}/review`, { method: 'POST' }),

  dismissReport: (reportId: string) =>
    apiJson<Report>(`/api/admin/reports/${reportId}/dismiss`, { method: 'POST' }),

  // recipes
  getAdminRecipes: (page = 1, size = 20) =>
    apiJson<AdminRecipePage>(`/api/admin/recipes?page=${page}&size=${size}`),

  hideRecipe: (recipeId: string, reason?: string) =>
    apiJson<AdminRecipe>(`/api/admin/recipes/${recipeId}/hide`, {
      method: 'POST',
      body: JSON.stringify({ reason: reason ?? null }),
    }),

  unhideRecipe: (recipeId: string) =>
    apiJson<AdminRecipe>(`/api/admin/recipes/${recipeId}/unhide`, {
      method: 'POST',
      body: JSON.stringify({}),
    }),

  // comments
  getAdminComments: (page = 1, size = 20) =>
    apiJson<AdminCommentPage>(`/api/admin/comments?page=${page}&size=${size}`),

  // audit
  getAuditLog: (page = 1, size = 20) =>
    apiJson<AuditPage>(`/api/admin/audit?page=${page}&size=${size}`),
}
