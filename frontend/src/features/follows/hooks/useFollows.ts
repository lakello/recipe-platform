import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { followsApi } from '../api/followsApi'

export const FOLLOWERS_KEY = (userId: string) => ['followers', userId]
export const FOLLOWING_KEY = (userId: string) => ['following', userId]
export const PUBLIC_USER_KEY = (userId: string) => ['publicUser', userId]

export function useFollowers(userId: string, page = 1) {
  return useQuery({
    queryKey: [...FOLLOWERS_KEY(userId), page],
    queryFn: () => followsApi.listFollowers(userId, page),
  })
}

export function useFollowing(userId: string, page = 1) {
  return useQuery({
    queryKey: [...FOLLOWING_KEY(userId), page],
    queryFn: () => followsApi.listFollowing(userId, page),
  })
}

export function useFollow(userId: string) {
  const queryClient = useQueryClient()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: PUBLIC_USER_KEY(userId) })
    queryClient.invalidateQueries({ queryKey: FOLLOWERS_KEY(userId) })
    queryClient.invalidateQueries({ queryKey: FOLLOWING_KEY(userId) })
  }

  const follow = useMutation({
    mutationFn: () => followsApi.follow(userId),
    onSuccess: invalidate,
  })

  const unfollow = useMutation({
    mutationFn: () => followsApi.unfollow(userId),
    onSuccess: invalidate,
  })

  return { follow, unfollow }
}
