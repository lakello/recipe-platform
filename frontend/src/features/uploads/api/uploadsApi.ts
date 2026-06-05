import { apiJson, apiFetch } from '@/shared/api/client'

export type UploadType = 'recipe_photo' | 'avatar'
export type ContentType = 'image/jpeg' | 'image/png' | 'image/webp'

export interface PresignResponse {
  upload_url: string
  key: string
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

  uploadToS3: (uploadUrl: string, file: File) =>
    fetch(uploadUrl, {
      method: 'PUT',
      headers: { 'Content-Type': file.type },
      body: file,
    }),

  attachRecipePhoto: (recipeId: string, key: string) =>
    apiJson(`/api/uploads/recipes/${recipeId}/photo`, {
      method: 'POST',
      body: JSON.stringify({ key }),
    }),

  deleteRecipePhoto: async (recipeId: string) => {
    const res = await apiFetch(`/api/uploads/recipes/${recipeId}/photo`, {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('Не удалось удалить фото')
  },

  setAvatar: (key: string) =>
    apiJson('/api/uploads/avatar', {
      method: 'POST',
      body: JSON.stringify({ key }),
    }),

  getViewUrl: (key: string) => `/api/uploads/view?key=${encodeURIComponent(key)}`,
}
