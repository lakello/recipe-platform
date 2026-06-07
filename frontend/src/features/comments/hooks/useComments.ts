import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { commentsApi } from '../api/commentsApi'

export const commentsKey = (recipeId: string) => ['comments', recipeId]
export const repliesKey = (commentId: string) => ['replies', commentId]

export function useComments(recipeId: string) {
  return useQuery({
    queryKey: commentsKey(recipeId),
    queryFn: () => commentsApi.list(recipeId),
  })
}

export function useReplies(commentId: string, enabled: boolean) {
  return useQuery({
    queryKey: repliesKey(commentId),
    queryFn: () => commentsApi.listReplies(commentId),
    enabled,
  })
}

export function useAddComment(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ body, parentId }: { body: string; parentId?: string }) =>
      commentsApi.create(recipeId, body, parentId),
    onSuccess: (_data, { parentId }) => {
      queryClient.invalidateQueries({ queryKey: commentsKey(recipeId) })
      if (parentId) {
        queryClient.invalidateQueries({ queryKey: repliesKey(parentId) })
      }
    },
  })
}

export function useEditComment(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ commentId, body }: { commentId: string; body: string }) =>
      commentsApi.update(commentId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: commentsKey(recipeId) })
    },
  })
}

export function useDeleteComment(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (commentId: string) => commentsApi.delete(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: commentsKey(recipeId) })
    },
  })
}

export function useHideComment(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (commentId: string) => commentsApi.hide(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: commentsKey(recipeId) })
    },
  })
}

export function useUnhideComment(recipeId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (commentId: string) => commentsApi.unhide(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: commentsKey(recipeId) })
    },
  })
}
