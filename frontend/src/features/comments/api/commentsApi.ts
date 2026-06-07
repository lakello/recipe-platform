import { apiJson, apiFetch } from '@/shared/api/client'

export interface CommentAuthor {
  id: string
  username: string
  avatar_url: string | null
}

export interface Comment {
  id: string
  recipe_id: string
  author_id: string
  parent_id: string | null
  body: string
  is_hidden: boolean
  is_deleted: boolean
  author: CommentAuthor
  reply_count: number
  created_at: string
  updated_at: string
}

export interface CommentPage {
  items: Comment[]
  total: number
  page: number
  size: number
  has_more: boolean
}

export const commentsApi = {
  list: (recipeId: string, page = 1, size = 20) =>
    apiJson<CommentPage>(
      `/api/recipes/${recipeId}/comments?page=${page}&size=${size}`,
    ),

  listReplies: (commentId: string, page = 1, size = 20) =>
    apiJson<CommentPage>(
      `/api/comments/${commentId}/replies?page=${page}&size=${size}`,
    ),

  create: (recipeId: string, body: string, parentId?: string) =>
    apiJson<Comment>(`/api/recipes/${recipeId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ body, parent_id: parentId ?? null }),
    }),

  update: (commentId: string, body: string) =>
    apiJson<Comment>(`/api/comments/${commentId}`, {
      method: 'PATCH',
      body: JSON.stringify({ body }),
    }),

  delete: async (commentId: string) => {
    const res = await apiFetch(`/api/comments/${commentId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Не удалось удалить комментарий')
  },

  hide: (commentId: string) =>
    apiJson<Comment>(`/api/comments/${commentId}/hide`, { method: 'POST' }),

  unhide: (commentId: string) =>
    apiJson<Comment>(`/api/comments/${commentId}/unhide`, { method: 'POST' }),
}
