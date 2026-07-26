import { apiJson, apiFetch } from '@/shared/api/client'

export type UploadType = 'recipe_photo' | 'avatar'
export type ContentType = 'image/jpeg' | 'image/png' | 'image/webp'

export interface PresignResponse {
  upload_id: string
  upload_url: string
  fields: Record<string, string>
  key: string
}

export interface UploadStatus {
  upload_id: string
  status: 'pending' | 'validating' | 'validated' | 'failed' | 'attached'
}

export const uploadsApi = {
  presign: (params: {
    upload_type: UploadType
    content_type: ContentType
    recipe_id?: string
  }) =>
    apiJson<PresignResponse>('/api/uploads/presign', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  uploadToS3: (uploadUrl: string, fields: Record<string, string>, file: File) => {
    const form = new FormData()
    Object.entries(fields).forEach(([key, value]) => form.append(key, value))
    form.append('file', file)
    return fetch(uploadUrl, { method: 'POST', body: form })
  },

  confirm: (uploadId: string) =>
    apiJson<UploadStatus>(`/api/uploads/${uploadId}/confirm`, { method: 'POST' }),

  status: (uploadId: string) =>
    apiJson<UploadStatus>(`/api/uploads/status/${uploadId}`),

  attachRecipePhoto: (recipeId: string, uploadId: string) =>
    apiJson(`/api/uploads/recipes/${recipeId}/photo`, {
      method: 'POST',
      body: JSON.stringify({ upload_id: uploadId }),
    }),

  deleteRecipePhoto: async (recipeId: string) => {
    const res = await apiFetch(`/api/uploads/recipes/${recipeId}/photo`, {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('Не удалось удалить фото')
  },

  setAvatar: (uploadId: string) =>
    apiJson('/api/uploads/avatar', {
      method: 'POST',
      body: JSON.stringify({ upload_id: uploadId }),
    }),

  getViewUrl: (key: string) => `/api/uploads/view?key=${encodeURIComponent(key)}`,
}
