import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { RECIPES_KEY } from '@/features/recipes/hooks/useRecipes'
import { CURRENT_USER_KEY } from '@/features/profile/hooks/useCurrentUser'
import { uploadsApi, type ContentType } from '../api/uploadsApi'

const ALLOWED_TYPES: ContentType[] = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE_MB = 10

function validateFile(file: File): string | null {
  if (!ALLOWED_TYPES.includes(file.type as ContentType)) {
    return 'Допустимые форматы: JPEG, PNG, WebP'
  }
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    return `Максимальный размер файла: ${MAX_SIZE_MB} МБ`
  }
  return null
}

export function useRecipePhotoUpload(recipeId: string) {
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const upload = async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }
    setError(null)
    setIsPending(true)
    try {
      const { upload_url, key } = await uploadsApi.presign({
        upload_type: 'recipe_photo',
        content_type: file.type as ContentType,
        recipe_id: recipeId,
      })
      const res = await uploadsApi.uploadToS3(upload_url, file)
      if (!res.ok) throw new Error('Ошибка при загрузке файла')
      await uploadsApi.attachRecipePhoto(recipeId, key)
      await queryClient.invalidateQueries({ queryKey: [...RECIPES_KEY, recipeId] })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки')
    } finally {
      setIsPending(false)
    }
  }

  const remove = async () => {
    setIsPending(true)
    try {
      await uploadsApi.deleteRecipePhoto(recipeId)
      await queryClient.invalidateQueries({ queryKey: [...RECIPES_KEY, recipeId] })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка удаления')
    } finally {
      setIsPending(false)
    }
  }

  return { upload, remove, isPending, error }
}

export function useAvatarUpload() {
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const upload = async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }
    setError(null)
    setIsPending(true)
    try {
      const { upload_url, key } = await uploadsApi.presign({
        upload_type: 'avatar',
        content_type: file.type as ContentType,
      })
      const res = await uploadsApi.uploadToS3(upload_url, file)
      if (!res.ok) throw new Error('Ошибка при загрузке файла')
      await uploadsApi.setAvatar(key)
      await queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки')
    } finally {
      setIsPending(false)
    }
  }

  return { upload, isPending, error }
}
